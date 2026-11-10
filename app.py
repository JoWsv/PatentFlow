import os, sqlite3, secrets, math
from datetime import date, timedelta
from functools import wraps
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort, g
from werkzeug.security import generate_password_hash, check_password_hash

ROOT = Path(__file__).resolve().parent
DB = ROOT / 'instance' / 'patentflow.sqlite3'
DB.parent.mkdir(exist_ok=True)
app = Flask(__name__)
app.config.update(SECRET_KEY=os.environ.get('SECRET_KEY', secrets.token_hex(32)), SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax', SESSION_COOKIE_SECURE=os.environ.get('COOKIE_SECURE') == '1', PERMANENT_SESSION_LIFETIME=timedelta(minutes=30), MAX_CONTENT_LENGTH=1024*128)
STATUSES = ['Em andamento', 'Aguardando', 'Concluído']
SITUACOES = ['Pendente', 'Em andamento', 'Concluída']

def db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys=ON')
    return g.db

@app.teardown_appcontext
def close_db(exc):
    conn=g.pop('db',None)
    if conn: conn.close()

@app.context_processor
def inject_csrf():
    if 'csrf' not in session: session['csrf']=secrets.token_urlsafe(32)
    return {'csrf_token':session['csrf']}

@app.before_request
def check_csrf():
    if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
        token_sessao = session.get('csrf')
        token_formulario = request.form.get('csrf_token')

        if not token_sessao or not token_formulario:
            abort(400, description='Token CSRF ausente.')

        if not secrets.compare_digest(token_sessao, token_formulario):
            abort(400, description='Token CSRF inválido.')

@app.after_request
def security_headers(response):
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['X-Frame-Options']='DENY'
    response.headers['Referrer-Policy']='strict-origin-when-cross-origin'
    response.headers['Content-Security-Policy']="default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
    return response

def init_db():
    with app.app_context():
        c=db()
        c.executescript("""CREATE TABLE IF NOT EXISTS usuario(id INTEGER PRIMARY KEY, nome TEXT UNIQUE NOT NULL, senha_hash TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS patente(id INTEGER PRIMARY KEY, numero_processo TEXT UNIQUE NOT NULL, inventor TEXT NOT NULL, instituto TEXT NOT NULL, data_registro TEXT NOT NULL, status TEXT NOT NULL, custos REAL NOT NULL DEFAULT 0 CHECK(custos >= 0));
CREATE TABLE IF NOT EXISTS etapa(id INTEGER PRIMARY KEY, id_patente INTEGER NOT NULL REFERENCES patente(id) ON DELETE CASCADE, descricao TEXT NOT NULL, prazo TEXT, situacao TEXT NOT NULL, data_conclusao TEXT);
CREATE INDEX IF NOT EXISTS idx_etapa_patente_prazo ON etapa(id_patente,prazo);""")
        c.commit()

def login_required(fn):
    @wraps(fn)
    def inner(*a,**kw):
        if not session.get('user'): return redirect(url_for('login'))
        return fn(*a,**kw)
    return inner

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        user=db().execute('SELECT * FROM usuario WHERE nome=?',(request.form.get('nome','').strip(),)).fetchone()
        if user and check_password_hash(user['senha_hash'],request.form.get('senha','')):
            session.clear();session['user']=user['nome'];session.permanent=True
            return redirect(url_for('index'))
        flash('Usuário ou senha inválidos.','erro')
    return render_template('login.html')

@app.post('/sair')
def sair():
    session.clear();return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    q=request.args.get('q','').strip()[:80]
    status=request.args.get('status','')
    sql='SELECT * FROM patente WHERE (numero_processo LIKE ? OR inventor LIKE ? OR instituto LIKE ?)'
    args=['%'+q+'%']*3
    if status in STATUSES:sql+=' AND status=?';args.append(status)
    sql+=' ORDER BY id DESC LIMIT 100'
    patents=[]
    for pat in db().execute(sql,args).fetchall():
        steps=db().execute("SELECT * FROM etapa WHERE id_patente=? AND situacao!='Concluída' ORDER BY (prazo IS NULL),prazo,id LIMIT 1",(pat['id'],)).fetchone()
        patents.append((pat,steps))
    return render_template('index.html',patents=patents,q=q,status=status,statuses=STATUSES)

def valid_date(s):
    try: return date.fromisoformat(s)
    except (ValueError,TypeError): return None

@app.route('/patentes/nova',methods=['GET','POST'])
@app.route('/patentes/<int:pid>/editar',methods=['GET','POST'])
@login_required
def form_patente(pid=None):
    pat=db().execute('SELECT * FROM patente WHERE id=?',(pid,)).fetchone() if pid else None
    if pid and not pat:abort(404)
    if request.method=='POST':
        f=request.form
        numero=f.get('numero_processo','').strip()[:60];inventor=f.get('inventor','').strip()[:120];instituto=f.get('instituto','').strip()[:120];dt=f.get('data_registro','');status=f.get('status','');raw=f.get('custos','0').replace(',','.')
        try:
         custos = float(raw)
         if not math.isfinite(custos):
             custos = -1
        except (ValueError, OverflowError):
            custos = -1
        if not numero or not inventor or not instituto or not valid_date(dt) or status not in STATUSES or custos<0:
            flash('Confira os campos obrigatórios, a data e o valor dos custos.','erro')
        else:
            try:
                if pid:
                    db().execute('UPDATE patente SET numero_processo=?,inventor=?,instituto=?,data_registro=?,status=?,custos=? WHERE id=?',(numero,inventor,instituto,dt,status,custos,pid))
                else:
                    cur=db().execute('INSERT INTO patente(numero_processo,inventor,instituto,data_registro,status,custos) VALUES(?,?,?,?,?,?)',(numero,inventor,instituto,dt,status,custos));pid=cur.lastrowid
                db().commit();flash('Patente salva com sucesso.','sucesso');return redirect(url_for('detalhes',pid=pid))
            except sqlite3.IntegrityError:flash('Este número de processo já está cadastrado.','erro')
    return render_template('form.html',pat=pat,statuses=STATUSES)

@app.route('/patentes/<int:pid>',methods=['GET','POST'])
@login_required
def detalhes(pid):
    pat=db().execute('SELECT * FROM patente WHERE id=?',(pid,)).fetchone()
    if not pat:abort(404)
    if request.method=='POST':
        f=request.form;descricao=f.get('descricao','').strip()[:200];prazo=f.get('prazo','').strip() or None;situacao=f.get('situacao','')
        if not descricao or (prazo and not valid_date(prazo)) or situacao not in SITUACOES:
            flash('Informe uma descrição, situação e prazo válido.','erro')
        else:
            db().execute('INSERT INTO etapa(id_patente,descricao,prazo,situacao,data_conclusao) VALUES(?,?,?,?,?)',(pid,descricao,prazo,situacao,date.today().isoformat() if situacao=='Concluída' else None));db().commit()
            flash('Etapa adicionada com sucesso.','sucesso');return redirect(url_for('detalhes',pid=pid))
    steps=db().execute('SELECT * FROM etapa WHERE id_patente=? ORDER BY (prazo IS NULL),prazo,id',(pid,)).fetchall()
    next_step=next((s for s in steps if s['situacao']!='Concluída'),None)
    return render_template('details.html',pat=pat,steps=steps,next_step=next_step,situacoes=SITUACOES,today=date.today().isoformat())

@app.post('/etapas/<int:eid>/concluir')
@login_required
def concluir(eid):
    step=db().execute('SELECT * FROM etapa WHERE id=?',(eid,)).fetchone()
    if not step:abort(404)
    db().execute("UPDATE etapa SET situacao='Concluída',data_conclusao=? WHERE id=?",(date.today().isoformat(),eid));db().commit()
    flash('Etapa concluída.','sucesso');return redirect(url_for('detalhes',pid=step['id_patente']))

@app.errorhandler(400)
def bad_request(error):return render_template('error.html',message='Não foi possível processar o formulário. Atualize a página e tente novamente.'),400
@app.errorhandler(404)
def not_found(error):return render_template('error.html',message='Página ou registro não encontrado.'),404

if __name__=='__main__':
    init_db()
    app.run(debug=False)
