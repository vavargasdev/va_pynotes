# Finalizando para publicação Github

### Revisão final do código
- Avaliar o código se tem alguma otimização importante antes de publicar
- Verificar os comentários se estão bem colocados, relevante e em ingles
- Comentar prints desnecessários de debug

### Inicialização do banco de dados
Criar um metodo em main_frame caso não tenha o banco de dados SQLite (migration)
Arquivo: /data/data_notes.db

Estrutura:
CREATE TABLE notas (
    codigo_id INTEGER PRIMARY KEY AUTOINCREMENT,
    categ     TEXT,
    titulo    TEXT,
    texto     TEXT,
    imagens   TEXT,
    data      DATE    DEFAULT (DATE('now') ) 
);

Criar duas notas no novo BD (em ingles):
1: 
categ: text,
titulo: Edit Notes
texto: Editar suas anotações aqui, lembretes ou trechos de código aqui. O título e categoria também podem ser alterados. Selecione uma categoria existente ou digite uma nova categoria no campo. As notas serão salvas automaticamente.
Para localizar uma nota use o campo acima e botões de categorias para filtrar. Serão exibidas as 10 notas mais recentes no filtro pesquisado.

2:
categ: vazio
titulo: Inserir Notas
Texto: Para novas notas clique no botão Add Note na esquerda e a direita surgirá uma nova nota, adicione título, categoria e texto.

### Criar um Readme em ingles
Criar um texto em README.md para apresentação no GitHub, simples mas bem informativo com as informações a seguir

Apresentação:
- Aplicação simples para edição de notas em texto
- Usando Python e WxPython
- Foco em usabilidade: fácil localização e visualização em categorias de diversas notas simutâneas
- Armazenamento das notas em SQLite em na pasta "/data" (o usuário pode copiar e armazenar para segurança)
- Interface clara e limpa
- Aplicação leve
- Uso de cores para detacar categorias das notas
- Incluir imagem da interface (VaPyNotes.png)
- Configuração de cores e numero de notas na tela em config.ini
- Em desenvolvimento
- Por enquanto testada no Windows

Instalação e uso:
- Como instalar Python e requerimentos
- Copiar aplicação para pasta
- Como criar Venv
- Como iniciar pelo console
- Como iniciar por arquivo Bat

A desenvolver:
- Paginação de resultados
- Ordenação de resultados
- Janela de configurações
- Melhor gerenciamento de categorias e cores
- Exportação do BD em CSV ou texto
- Formatação MD (?)
- Colorização de códigos (?)