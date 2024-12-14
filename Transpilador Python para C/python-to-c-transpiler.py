import re
import sys
import ast
from typing import List, Dict, Any

class PythonToCTranspiler:
    def __init__(self):
        # Mapeamento de tipos e estruturas
        self.indent_level = 0
        self.variables: Dict[str, str] = {}  # Nome da variável -> tipo
        self.functions: Dict[str, Dict[str, Any]] = {}
        self.imported_libs = set(['stdio.h', 'stdbool.h', 'string.h', 'stdlib.h'])

    def infer_type(self, value: str) -> str:
        """Infere o tipo de uma variável de forma mais robusta"""
        value = value.strip()
        
        # Strings
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            return 'char*'
        
        # Booleanos
        if value.lower() in ['true', 'false']:
            return 'bool'
        
        # Números inteiros
        if re.match(r'^-?\d+$', value):
            return 'int'
        
        # Números de ponto flutuante
        if re.match(r'^-?\d+\.\d+$', value):
            return 'float'
        
        # Listas
        if value.startswith('[') and value.endswith(']'):
            return 'int*'  # Simplificado, poderia ser mais complexo
        
        # Se não conseguir inferir, assume genérico
        return 'void*'

    def generate_header(self) -> List[str]:
        """Gera cabeçalho do código C com bibliotecas importadas"""
        header = []
        for lib in sorted(self.imported_libs):
            header.append(f'#include <{lib}>')
        header.append('')
        return header

    def transpile_expression(self, node: ast.AST) -> str:
        """Transpila expressões de forma mais robusta"""
        if isinstance(node, ast.Num):
            return str(node.n)
        
        elif isinstance(node, ast.Str):
            return node.s
        
        elif isinstance(node, ast.Name):
            return node.id
        
        elif isinstance(node, ast.BinOp):
            left = self.transpile_expression(node.left)
            right = self.transpile_expression(node.right)
            
            if isinstance(node.op, ast.Add):
                return f'({left} + {right})'
            elif isinstance(node.op, ast.Sub):
                return f'({left} - {right})'
            elif isinstance(node.op, ast.Mult):
                return f'({left} * {right})'
            elif isinstance(node.op, ast.Div):
                return f'({left} / {right})'
        
        elif isinstance(node, ast.Compare):
            left = self.transpile_expression(node.left)
            ops = node.ops
            comparators = node.comparators
            
            if len(ops) == 1:
                op = ops[0]
                right = self.transpile_expression(comparators[0])
                
                if isinstance(op, ast.Lt):
                    return f'({left} < {right})'
                elif isinstance(op, ast.LtE):
                    return f'({left} <= {right})'
                elif isinstance(op, ast.Gt):
                    return f'({left} > {right})'
                elif isinstance(op, ast.GtE):
                    return f'({left} >= {right})'
                elif isinstance(op, ast.Eq):
                    return f'({left} == {right})'
        
        return str(node)

    def transpile_statement(self, node: ast.AST) -> List[str]:
        """Transpila diferentes tipos de declarações"""
        lines = []
        indent = "    " * self.indent_level

        if isinstance(node, ast.Assign):
            # Suporta atribuição simples
            target = node.targets[0]
            value = self.transpile_expression(node.value)
            
            if isinstance(target, ast.Name):
                var_name = target.id
                var_type = self.infer_type(value)
                
                # Primeira declaração
                if var_name not in self.variables:
                    lines.append(f"{indent}{var_type} {var_name} = {value};")
                    self.variables[var_name] = var_type
                else:
                    # Já declarada
                    lines.append(f"{indent}{var_name} = {value};")
        
        elif isinstance(node, ast.If):
            # Transpilação de If
            test = self.transpile_expression(node.test)
            lines.append(f"{indent}if ({test}) {{")
            self.indent_level += 1
            
            for body_node in node.body:
                lines.extend(self.transpile_statement(body_node))
            
            if node.orelse:
                lines.append(f"{indent[:-4]}}} else {{")
                for else_node in node.orelse:
                    lines.extend(self.transpile_statement(else_node))
            
            self.indent_level -= 1
            lines.append(f"{indent}}}")
        
        elif isinstance(node, ast.For):
            # Transpilação de For (simplificado para range)
            if isinstance(node.iter, ast.Call) and \
               isinstance(node.iter.func, ast.Name) and \
               node.iter.func.id == 'range':
                
                # Assume range com 1 ou 2 argumentos
                if len(node.iter.args) == 1:
                    start, end = 0, self.transpile_expression(node.iter.args[0])
                else:
                    start = self.transpile_expression(node.iter.args[0])
                    end = self.transpile_expression(node.iter.args[1])
                
                target = node.target.id
                lines.append(f"{indent}for (int {target} = {start}; {target} < {end}; {target}++) {{")
                self.indent_level += 1
                
                for body_node in node.body:
                    lines.extend(self.transpile_statement(body_node))
                
                self.indent_level -= 1
                lines.append(f"{indent}}}")
        
        elif isinstance(node, ast.Expr):
            # Chamadas de função ou outras expressões
            if isinstance(node.value, ast.Call):
                func_name = node.value.func.id
                args = [self.transpile_expression(arg) for arg in node.value.args]
                lines.append(f"{indent}{func_name}({', '.join(args)});")
        
        return lines

    def transpile(self, python_code: str) -> str:
        """Transpila o código Python completo"""
        try:
            # Parse o código Python para uma AST
            tree = ast.parse(python_code)
            
            # Gera código C
            c_code = self.generate_header()
            c_code.append("int main() {")
            
            # Transpila cada nó da árvore
            for node in tree.body:
                c_code.extend(self.transpile_statement(node))
            
            c_code.append("    return 0;")
            c_code.append("}")
            
            return "\n".join(c_code)
        
        except SyntaxError as e:
            print(f"Erro de sintaxe no código Python: {e}")
            return ""
        except Exception as e:
            print(f"Erro durante a transpilação: {e}")
            return ""

def transpile_file(input_file: str, output_file: str):
    """Transpila um arquivo Python inteiro"""
    with open(input_file, 'r') as f:
        python_code = f.read()
    
    transpiler = PythonToCTranspiler()
    c_code = transpiler.transpile(python_code)
    
    with open(output_file, 'w') as f:
        f.write(c_code)
    
    print(f"Transpilação concluída. Código C gerado em {output_file}")

def main():
    # Exemplo de uso
    python_code = """
x = 10
y = 20
if x < y:
    z = x + y
    print(z)
else:
    z = x - y
    print(z)

for i in range(5):
    print(i)
    """

    transpiler = PythonToCTranspiler()
    c_code = transpiler.transpile(python_code)
    print(c_code)

if __name__ == "__main__":
    main()
