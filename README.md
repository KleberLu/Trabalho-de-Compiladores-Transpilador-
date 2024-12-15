# Transpilador

O repositório apresenta um transpilador desenvolvido para converter código escrito em Python para a linguagem C. Ele utiliza a biblioteca ast (Abstract Syntax Tree) do Python para análise e geração do código-fonte equivalente em C.

##  Componentes do grupo

- Dyelle Hemylle Nunes de Almeida
- Ingrid Gabrielly Camara Lira
- Kléber Lucas Lopes Alves
- Tállyson Emanoel Roques Izidio
- Vitor Eduardo de Carvalho

## 🚀 Como Usar

Para clonar o repositório e executar o projeto localmente, siga estas etapas:

1. **Instale as dependências:** certifique-se de que o Python está instalado no sistema. Em seguida, instale o módulo typing:


    ```bash
    pip install typing
    ```

2. **Configure o código a ser transpilado:** abra o arquivo principal e localize o método main na linha 206:

    ```bash
    def main():
    ```
**OBS:** Substitua o código entre as linhas 209 e 219 pelo código Python que deseja transpilar.

3. **Execute o transpilador:** No terminal do Visual Studio Code (ou outro ambiente), execute o script. O transpilador irá gerar um código equivalente em C.


## 🔎 Estrutura do Projeto
**Biblioteca AST**: Utilizada para análise sintática e léxica do código Python.

**Exemplo de código em Python:**

```bash
for i in range(5):
    if i < 3:
        print("Menor que 3")
    else:
        print("Maior ou igual a 3")
```

**Geração de código para linguagem C:**

```bash
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
for (int i = 0; i < 5; i++) {
    if ((i < 3)) {
        print(Menor que 3);
} else {
        print(Maior ou igual a 3);
    }
}
    return 0;
}
```