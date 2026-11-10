import getpass
from app import app,db,init_db
from werkzeug.security import generate_password_hash
init_db()
name=input('Nome de usuário administrador: ').strip()
password=getpass.getpass('Senha (mínimo 5 caracteres): ')
if not name or len(password)<5:raise SystemExit('Informe um nome e uma senha com pelo menos 5 caracteres.')
with app.app_context():
    db().execute('INSERT INTO usuario(nome,senha_hash) VALUES(?,?)',(name,generate_password_hash(password,method='scrypt')))
    db().commit()
print('Administrador criado com sucesso.')
