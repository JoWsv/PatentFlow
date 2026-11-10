# PatentFlow — MVP acadêmico
## Sobre o projeto

O PatentFlow é uma aplicação web desenvolvida para organizar e acompanhar processos de patentes. O sistema facilita o cadastro de informações, o controle das etapas e a identificação de atividades pendentes.

O projeto foi desenvolvido como parte da Experiência Prática do curso de Análise e Desenvolvimento de Sistemas.

## Tecnologias utilizadas

- Python e Flask
- SQLite
- HTML e CSS
- Git e GitHub

## Funcionalidades

- Login do administrador
- Cadastro de patentes
- Consulta e pesquisa de processos
- Edição das informações cadastradas
- Registro de etapas e prazos
- Identificação da próxima atividade pendente

## Telas do sistema

1. **Visão geral:** apresenta os processos cadastrados e permite iniciar um novo cadastro.
2. **Cadastro:** permite registrar informações de uma patente.
3. **Detalhes:** apresenta as informações, etapas, prazos e atividades pendentes.

## Executar localmente

1. Instale uma versão do Python compatível com as dependências.
2. Crie um ambiente virtual: `python -m venv .venv`.
3. Ative o ambiente:
   - Windows: `.venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`
4. Instale as dependências: `pip install -r requirements.txt`.
5. Crie uma conta de administrador: `python create_admin.py`.
6. Execute: `python -m flask --app app run`.
7. Acesse `http://127.0.0.1:5000`.

## Segurança

O sistema utiliza autenticação, hash de senhas, proteção CSRF e validação de entradas.

O banco de dados `instance/patentflow.sqlite3`, as senhas e as chaves secretas não devem ser publicados no GitHub.

O MVP utiliza dados fictícios e está destinado inicialmente à demonstração local. Antes de uma implantação pública, será necessário configurar HTTPS, uma SECRET_KEY persistente, cookies seguros, armazenamento persistente, limitação de tentativas de login e testes de segurança.

## Qualidade de software

O desenvolvimento utiliza Git e GitHub para controle de versão. Os testes automatizados, a integração contínua e as revisões por Pull Request serão documentados conforme sua implementação.

## Objetivo

Contribuir para a organização dos processos de patentes, facilitando o acompanhamento das atividades e dos prazos.
