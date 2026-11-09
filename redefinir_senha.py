
import getpass
from app import app, db, init_db
from werkzeug.security import generate_password_hash

init_db()

nome = input("Nome do administrador: ").strip()
senha = getpass.getpass("Nova senha (mínimo 5 caracteres): ")

if len(senha) < 5:
    raise SystemExit("A senha deve ter pelo menos 5 caracteres.")

with app.app_context():
    conexao = db()
    resultado = conexao.execute(
        "UPDATE usuario SET senha_hash = ? WHERE nome = ?",
        (generate_password_hash(senha, method="scrypt"), nome)
    )
    conexao.commit()

    if resultado.rowcount == 0:
        print("Usuário não encontrado. Verifique o nome digitado.")
    else:
        print("Senha atualizada com sucesso!")
