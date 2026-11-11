# ToDo App

Aplicação de lista de tarefas utilizada nos laboratórios de Engenharia de Software do professor Laércio. O objetivo do laboratório é trabalhar a implantação de uma aplicação em nuvem, partindo de um sistema já desenvolvido.

A aplicação permite cadastrar, listar, concluir, reabrir e excluir tarefas. Ela foi trazida do repositório `aula-uniamerica-infraestrutura-cloud` como base para este novo laboratório.

## Escopo para a Feira de Profissões

O cenário da atividade apresenta o projeto desenvolvido por alunos do 3º período de Engenharia de Software e a contratação de um profissional para implantá-lo na nuvem para a feira.

Consulte o [escopo em PDF](escopo.pdf) ou a [versão editável](docs/escopo.md), com arquitetura, automação, custos, entregáveis e critérios de aceite. O [fluxo proposto da aplicação](docs/assets/fluxo-aplicacao.pdf) também está disponível separadamente. Para gerar os PDFs, instale a dependência de documentação `reportlab` e execute `python scripts/render-escopo.py`.

## Executar localmente

Pré-requisitos: Git e Docker com Docker Compose. No Windows, execute o Docker Desktop com containers Linux antes de iniciar.

1. Abra um terminal na pasta deste repositório:

   ```bash
   cd todo-app
   ```

2. Construa as imagens e inicie os serviços:

   ```bash
   docker compose up --build -d
   ```

3. Confira os serviços e acompanhe os logs:

   ```bash
   docker compose ps
   docker compose logs -f
   ```

   Aguarde a mensagem `Conectado ao MongoDB` no backend. Use `Ctrl+C` para sair dos logs; os serviços continuam rodando.

4. Acesse a aplicação em **http://localhost**. A API está em **http://localhost:5000/todos**.

5. Cadastre uma tarefa, clique no texto para concluir ou reabrir e use **Excluir** para removê-la. Atualize a página para conferir os dados retornados pela API.

6. Ao terminar, pare os serviços:

   ```bash
   docker compose down
   ```

As portas 80, 5000 e 27017 precisam estar disponíveis na máquina. Caso seu ambiente use o executável legado, substitua `docker compose` por `docker-compose`.

## Estrutura

- `frontend/`: interface React, compilada e servida pelo Nginx.
- `backend/`: API Node.js com Express e Mongoose.
- `banco-de-dados/`: imagem MongoDB e script de criação dos dados iniciais.
- `docker-compose.yaml`: execução dos três serviços na rede local `todo-net`.

O navegador acessa o frontend e envia as operações para a API. A API consulta e atualiza o MongoDB.

```text
Navegador -> Frontend (porta 80)
Navegador -> API Express (porta 5000) -> MongoDB (porta 27017)
```

## Base do laboratório de nuvem

Esta importação mantém o código e a configuração de execução da aplicação original. O frontend utiliza `http://localhost:5000` para acessar a API, e a conexão do backend com o banco está definida em `backend/index.js`.

O Compose atual utiliza credenciais de demonstração e não configura um volume nomeado para o MongoDB. Endereços dos serviços, configuração por ambiente, persistência, isolamento do banco e automação da infraestrutura serão tratados no desenho do laboratório de nuvem.
