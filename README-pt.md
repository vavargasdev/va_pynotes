<div align="right">
<a href="./README.md">Read in English</a>
</div>

# VaPyNotes - Uma Aplicação Simples de Anotações em Python

VaPyNotes é uma aplicação de desktop para criar e gerenciar anotações baseadas em texto, construída com Python e o toolkit de GUI wxPython.

O foco principal é a usabilidade, permitindo a recuperação rápida e a visualização simultânea de múltiplas anotações organizadas por categorias.

## Funcionalidades

-   **Edição Simples de Anotações**: Uma interface limpa para escrever e editar anotações de texto.
-   **Organização por Categorias**: Atribua categorias às anotações e filtre-as facilmente. As categorias são codificadas por cores para rápida identificação visual.
-   **Busca Rápida**: Encontre rapidamente anotações por título ou conteúdo.
-   **Armazenamento Local**: As anotações são salvas em um arquivo de banco de dados SQLite local (`data/data_notes.db`). Você pode facilmente fazer backup de suas anotações copiando este arquivo.
-   **Interface Limpa e Leve**: Uma UI mínima que não atrapalha seu fluxo de trabalho.
-   **Customizável**: Configure as cores da interface e o número de anotações exibidas na tela através do arquivo `data/config.ini`.

![PyNotes Application Screenshot](https://raw.githubusercontent.com/vavargasdev/va_pynotes/refs/heads/main/PyNotesSS.jpg)

## Status

**Em desenvolvimento**. Atualmente testado apenas no Windows.

## Instalação e Uso

### Pré-requisitos

-   Python 3.x
-   pip (instalador de pacotes do Python)

### Passos

1.  **Clone ou baixe o repositório:**
    ```bash
    git clone https://github.com/vavargasdev/va_pynotes.git
    cd va_pynotes
    ```

2.  **Crie um Ambiente Virtual (Recomendado):**
    É uma boa prática criar um ambiente virtual para gerenciar as dependências do projeto.
    ```bash
    # Crie o ambiente
    python -m venv venv

    # Ative-o
    # No Windows
    .\venv\Scripts\activate
    # No macOS/Linux
    source venv/bin/activate
    ```

3.  **Instale os Requisitos:**
    Instale os pacotes Python necessários. Por enquanto, wxpython.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute a Aplicação:**
    Você pode iniciar a aplicação a partir do console ou usando um arquivo de lote.

    -   **Pelo console:**
        ```bash
        python main.py
        ```

    -   **Usando um arquivo `.bat` (no Windows):**
        O repositório inclui um arquivo `run.bat`. Após instalar os requisitos dentro do ambiente virtual, você pode simplesmente dar um duplo clique neste arquivo para iniciar a aplicação.
        ```batch
        @echo off
        .\venv\Scripts\python.exe main.py
        ```

## Desenvolvimento Futuro (Roadmap)

-   [ ] Paginação de resultados
-   [ ] Opções avançadas de ordenação (por data, título, etc.)
-   [ ] Uma janela de configurações dedicada dentro do app
-   [ ] Melhores ferramentas de gerenciamento de categorias e cores
-   [ ] Exportar banco de dados para arquivos CSV ou texto plano
-   [ ] Suporte à formatação Markdown para anotações
-   [ ] Destaque de sintaxe para trechos de código