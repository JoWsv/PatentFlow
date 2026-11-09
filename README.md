# PatentFlow — MVP acadêmico

Aplicação web em português para cadastro e acompanhamento de processos de patentes, com dados fictícios.

## Executar localmente

1. Instale Python 3.12.
2. Na pasta do projeto, crie o ambiente: `python -m venv .venv`.
3. Ative-o: Windows `.venv\Scripts\activate`; macOS/Linux `source .venv/bin/activate`.
4. Instale: `pip install -r requirements.txt`.
5. Defina uma `SECRET_KEY` aleatória e persistente no ambiente antes de executar em produção. Exemplo de geração: `python -c "import secrets; print(secrets.token_hex(32))"`.
6. Crie a conta: `python create_admin.py`.
7. Execute: `python app.py` e acesse `http://127.0.0.1:5000`.

O banco é criado em `instance/patentflow.sqlite3` e não deve ser publicado no GitHub. A aplicação usa SQLite e foi pensada para demonstração local com poucos usuários. Para hospedagem, é necessário serviço com suporte a Python, HTTPS, variável `SECRET_KEY`, `COOKIE_SECURE=1` e armazenamento persistente. GitHub Pages **não executa Flask**.

## Segurança e limites

Login com hash scrypt, CSRF em formulários, SQL parametrizado, escape padrão Jinja2, cabeçalhos de segurança, cookies HttpOnly e SameSite. A limitação de tentativas de login, sessões revogáveis no servidor e testes automatizados ainda precisam ser implementados antes de uma implantação pública. Não insira informações reais ou confidenciais.

## Fluxo

1. Entrar com conta de demonstração criada localmente.
2. Cadastrar uma patente.
3. Abrir os detalhes e adicionar etapas.
4. A próxima atividade é a etapa não concluída com o prazo mais próximo.
