import os
import re
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)  

def get_db_connection():
    try:
        conexao_bd = mysql.connector.connect(
            host="localhost",
            user="root",
            senha="1234",
            database="zetria",
            port=3307,
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        return conexao_bd
    except mysql.connector.Error as erro_bd:
        print(f"Erro de conexão com o MySQL: {erro_bd}")
        flash(f"Erro crítico de conexão com o banco de dados: {erro_bd}", "danger")
        return None

def login_required(funcao_original):
    @wraps(funcao_original)
    def funcao_decorada(*args, **kwargs):
        if 'id_usuario' not in session:
            flash('Você precisa fazer login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return funcao_original(*args, **kwargs)
    return funcao_decorada

def extract_links(conteudo):
    return re.findall(r"\[\[([^\]]+)\]\]", conteudo)

def extract_tags(conteudo):
    return re.findall(r"(?:\s|^)

@app.route('/')
def index():
    if 'id_usuario' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome_usuario = request.form['nome_usuario']
        senha = request.form['senha']
        confirmar_senha = request.form.get('confirmar_senha', '')

        if senha != confirmar_senha:
            flash('As senhas não coincidem.', 'danger')
            return render_template('Cadastro.html')

        senha_hash = generate_password_hash(senha)
        conexao_bd = get_db_connection()
        cursor_db = None
        if conexao_bd:
            try:
                cursor_db = conexao_bd.cursor_db()
                cursor_db.execute(
                    "INSERT INTO usuarios (nome_usuario, hash_senha) VALUES (%s, %s)", (nome_usuario, senha_hash))
                conexao_bd.commit()
                flash('Usuário registrado com sucesso! Faça o login.', 'success')
                return redirect(url_for('login'))
            except mysql.connector.IntegrityError:
                flash('Nome de usuário já existe.', 'danger')
            except mysql.connector.Error as erro_bd:
                flash(f"Erro ao registrar: {erro_bd}", 'danger')
            finally:
                if cursor_db:
                    cursor_db.close()
                conexao_bd.close()
        else:
            flash('Erro ao conectar ao banco de dados.', 'danger')

    return render_template('Cadastro.html')

@app.route('/interface')
@login_required
def interface():
    return render_template('interface.html', nome_usuario=session['nome_usuario'])

@app.route('/notas')
@login_required
def notas():
    return render_template('Interface.notas.html', nome_usuario=session['nome_usuario'])

@app.route('/nota')
@login_required
def nota():
    return render_template('nota.html', nome_usuario=session['nome_usuario'])

@app.route('/flashcards')
@login_required
def flashcards():
    return render_template('interface.flashcard1.html', nome_usuario=session['nome_usuario'])

@app.route('/flashcards2')
@login_required
def flashcards2():
    return render_template('interface.flashcard2.html', nome_usuario=session['nome_usuario'])

@app.route('/flashcards3')
@login_required
def flashcards3():
    return render_template('interface.flashcard3.html', nome_usuario=session['nome_usuario'])

@app.route('/calendario')
@login_required
def calendario():
    return render_template('calendario.html', nome_usuario=session['nome_usuario'])

@app.route('/grafos')
@login_required
def grafos():
    return render_template('grafos.html', nome_usuario=session['nome_usuario'])

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome_usuario = request.form['nome_usuario']
        senha = request.form['senha']
        senha_hash = generate_password_hash(senha)
        conexao_bd = get_db_connection()
        cursor_db = None
        if conexao_bd:
            try:
                cursor_db = conexao_bd.cursor_db()
                cursor_db.execute(
                    "INSERT INTO usuarios (nome_usuario, hash_senha) VALUES (%s, %s)", (nome_usuario, senha_hash))
                conexao_bd.commit()
                flash('Usuário registrado com sucesso! Faça o login.', 'success')
                return redirect(url_for('login'))
            except mysql.connector.IntegrityError:
                flash('Nome de usuário já existe.', 'danger')
            except mysql.connector.Error as erro_bd:
                flash(f"Erro ao registrar: {erro_bd}", 'danger')
            finally:
                if cursor_db:
                    cursor_db.close()
                conexao_bd.close()
        else:
            flash('Erro ao conectar ao banco de dados.', 'danger')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nome_usuario = request.form['nome_usuario']
        senha = request.form['senha']
        conexao_bd = get_db_connection()
        cursor_db = None
        if conexao_bd:
            try:
                cursor_db = conexao_bd.cursor_db(dictionary=True)
                cursor_db.execute(
                    "SELECT * FROM usuarios WHERE nome_usuario = %s", (nome_usuario,))
                usuario_db = cursor_db.fetchone()
                if usuario_db and check_password_hash(usuario_db['hash_senha'], senha):
                    session['id_usuario'] = usuario_db['id_registro']
                    session['nome_usuario'] = usuario_db['nome_usuario']
                    flash('Login bem-sucedido!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Nome de usuário ou senha inválidos.', 'danger')
            except mysql.connector.Error as erro_bd:
                flash(f"Erro ao fazer login: {erro_bd}", 'danger')
            finally:
                if cursor_db:
                    cursor_db.close()
                conexao_bd.close()
        else:
            flash('Erro ao conectar ao banco de dados.', 'danger')

    if 'id_usuario' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('id_usuario', None)
    session.pop('nome_usuario', None)
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    id_usuario = session['id_usuario']
    conexao_bd = get_db_connection()
    notas = []
    if conexao_bd:
        cursor_db = conexao_bd.cursor_db(dictionary=True)
        try:
            cursor_db.execute(, (id_usuario,))
            notas = cursor_db.fetchall()
        except mysql.connector.Error as erro_bd:
            flash(f"Erro ao buscar notas: {erro_bd}", "danger")
        finally:
            cursor_db.close()
            conexao_bd.close()

    return render_template('dashboard.html', nome_usuario=session['nome_usuario'], notes=notas)

def process_note_links_tags(conexao_bd, cursor_db, id_nota, conteudo):
    id_usuario = session['id_usuario']
    titulos_notas_ligadas = extract_links(conteudo)
    ids_notas_destino = []
    if titulos_notas_ligadas:
        strings_formato = ','.join(['%s'] * len(titulos_notas_ligadas))
        consulta = f"SELECT id_registro FROM notas WHERE id_usuario = %s AND titulo IN ({strings_formato})"
        parametros = [id_usuario] + titulos_notas_ligadas
        cursor_db.execute(consulta, parametros)
        notas_destino = cursor_db.fetchall()
        ids_notas_destino = [nota[0] for nota in notas_destino]

    cursor_db.execute(
        "DELETE FROM links_notas WHERE id_nota_origem = %s", (id_nota,))
    if ids_notas_destino:
        dados_link = [(id_nota, id_destino)
                      for id_destino in ids_notas_destino if id_destino != id_nota]
        if dados_link:
            cursor_db.executemany(
                "INSERT IGNORE INTO links_notas (id_nota_origem, id_nota_destino) VALUES (%s, %s)", dados_link)

    nomes_etiquetas = list(set(extract_tags(conteudo)))
    ids_etiquetas = []
    for nome_etiqueta in nomes_etiquetas:
        cursor_db.execute(
            "INSERT IGNORE INTO etiquetas (name) VALUES (%s)", (nome_etiqueta,))
        cursor_db.execute("SELECT id_registro FROM etiquetas WHERE name = %s", (nome_etiqueta,))
        resultado_id_etiqueta = cursor_db.fetchone()
        if resultado_id_etiqueta:
            ids_etiquetas.append(resultado_id_etiqueta[0])

    cursor_db.execute("DELETE FROM nota_tags WHERE nota_id = %s", (id_nota,))
    if ids_etiquetas:
        dados_link_etiquetas = [(id_nota, id_tag) for id_tag in ids_etiquetas]
        cursor_db.executemany(
            "INSERT IGNORE INTO nota_tags (nota_id, tag_id) VALUES (%s, %s)", dados_link_etiquetas)

@app.route('/notessave', methods=['POST'])
@login_required
def save_note():
    id_usuario = session['id_usuario']
    titulo = request.form['titulo']
    conteudo = request.form['conteudo']
    conexao_bd = get_db_connection()
    cursor_db = None
    if conexao_bd:
        try:
            cursor_db = conexao_bd.cursor_db()
            cursor_db.execute(
                "INSERT INTO notas (id_usuario, titulo, conteudo) VALUES (%s, %s, %s)", (id_usuario, titulo, conteudo))
            id_nota = cursor_db.lastrowid
            process_note_links_tags(conexao_bd, cursor_db, id_nota, conteudo)
            conexao_bd.commit()
            flash('Nota salva com sucesso!', 'success')
        except mysql.connector.Error as erro_bd:
            flash(f"Erro ao salvar nota: {erro_bd}", "danger")
            conexao_bd.rollback()
        finally:
            cursor_db.close()
            conexao_bd.close()
    else:
        flash('Erro ao conectar ao banco de dados para salvar nota.', 'danger')

    return redirect(url_for('dashboard'))

@app.route('/notes<int:id_nota>')
@login_required
def view_note(id_nota):
    id_usuario = session['id_usuario']
    conexao_bd = get_db_connection()
    nota, etiquetas, notas_linkadas, notas_que_linkam = None, [], [], []
    if conexao_bd:
        cursor_db = conexao_bd.cursor_db(dictionary=True)
        try:
            cursor_db.execute(
                "SELECT * FROM notas WHERE id_registro = %s AND id_usuario = %s", (id_nota, id_usuario))
            nota = cursor_db.fetchone()
            if not nota:
                flash('Nota não encontrada ou acesso não permitido.', 'warning')
                return redirect(url_for('dashboard'))

            cursor_db.execute(
                "SELECT etiqueta_item.name FROM etiquetas etiqueta_item JOIN nota_tags nota_etiqueta_item ON etiqueta_item.id_registro = nota_etiqueta_item.tag_id WHERE nota_etiqueta_item.nota_id = %s", (id_nota,))
            etiquetas = [linha['name'] for linha in cursor_db.fetchall()]

            cursor_db.execute(
                "SELECT nota_item.id_registro, nota_item.titulo FROM notas nota_item JOIN links_notas link_nota_item ON nota_item.id_registro = link_nota_item.id_nota_destino WHERE link_nota_item.id_nota_origem = %s", (id_nota,))
            notas_linkadas = cursor_db.fetchall()

            cursor_db.execute(
                "SELECT nota_item.id_registro, nota_item.titulo FROM notas nota_item JOIN links_notas link_nota_item ON nota_item.id_registro = link_nota_item.id_nota_origem WHERE link_nota_item.id_nota_destino = %s", (id_nota,))
            notas_que_linkam = cursor_db.fetchall()
        except mysql.connector.Error as erro_bd:
            flash(f"Erro ao buscar detalhes da nota: {erro_bd}", "danger")
        finally:
            cursor_db.close()
            conexao_bd.close()
    else:
        flash('Erro ao conectar ao banco de dados.', 'danger')

    return render_template('view_note.html', note=nota, etiquetas=etiquetas, notas_ligadas=notas_linkadas, notas_que_ligam=notas_que_linkam)

@app.route('/notesedit<int:id_nota>', methods=['GET', 'POST'])
@login_required
def edit_note(id_nota):
    id_usuario = session['id_usuario']
    conexao_bd = get_db_connection()
    if not conexao_bd:
        flash('Erro ao conectar ao banco de dados.', 'danger')
        return redirect(url_for('dashboard'))

    cursor_db = conexao_bd.cursor_db(dictionary=True)
    try:
        cursor_db.execute(
            "SELECT * FROM notas WHERE id_registro = %s AND id_usuario = %s", (id_nota, id_usuario))
        nota = cursor_db.fetchone()
        if not nota:
            flash('Nota não encontrada ou acesso não permitido.', 'warning')
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            titulo = request.form['titulo']
            conteudo = request.form['conteudo']
            cursor_db.execute(
                "UPDATE notas SET titulo = %s, conteudo = %s WHERE id_registro = %s", (titulo, conteudo, id_nota))
            process_note_links_tags(conexao_bd, cursor_db, id_nota, conteudo)
            conexao_bd.commit()
            flash('Nota atualizada com sucesso!', 'success')
            return redirect(url_for('view_note', id_nota=id_nota))
    except mysql.connector.Error as erro_bd:
        flash(f"Erro ao editar nota: {erro_bd}", "danger")
        conexao_bd.rollback()
    finally:
        cursor_db.close()
        conexao_bd.close()

    return render_template('edit_note.html', note=nota)

@app.route('/notesdelete<int:id_nota>', methods=['POST'])
@login_required
def delete_note(id_nota):
    id_usuario = session['id_usuario']
    conexao_bd = get_db_connection()
    if not conexao_bd:
        flash('Erro ao conectar ao banco de dados.', 'danger')
        return redirect(url_for('dashboard'))

    cursor_db = conexao_bd.cursor_db()
    try:
        cursor_db.execute(
            "DELETE FROM notas WHERE id_registro = %s AND id_usuario = %s", (id_nota, id_usuario))
        conexao_bd.commit()
        if cursor_db.rowcount > 0:
            flash('Nota excluída com sucesso!', 'success')
        else:
            flash('Nota não encontrada ou acesso não permitido.', 'warning')
    except mysql.connector.Error as erro_bd:
        flash(f"Erro ao excluir nota: {erro_bd}", "danger")
        conexao_bd.rollback()
    finally:
        cursor_db.close()
        conexao_bd.close()

    return redirect(url_for('dashboard'))

@app.route('/search')
@login_required
def search_notes():
    id_usuario = session['id_usuario']
    consulta = request.args.get('q', '/')
    resultados = []
    conexao_bd = get_db_connection()
    if conexao_bd and consulta:
        try:
            cursor_db = conexao_bd.cursor_db(dictionary=True)
            termo_busca = f"%{consulta}%"
            sql_consulta = 
            cursor_db.execute(sql_consulta, (id_usuario, termo_busca, termo_busca, consulta))
            resultados = cursor_db.fetchall()
        except mysql.connector.Error as erro_bd:
            flash(f"Erro ao buscar notas: {erro_bd}", "danger")
        finally:
            cursor_db.close()
            conexao_bd.close()

    return render_template('search_results.html', consulta=consulta, resultados=resultados)

@app.route('/graph')
@login_required
def view_graph():
    return render_template('graph.html')

@app.route('/graph_data')
@login_required
def graph_data():
    id_usuario = session['id_usuario']
    nos, arestas = [], []
    conexao_bd = get_db_connection()
    if conexao_bd:
        try:
            cursor_db = conexao_bd.cursor_db(dictionary=True)
            cursor_db.execute(
                "SELECT id_registro, titulo FROM notas WHERE id_usuario = %s", (id_usuario,))
            notas = cursor_db.fetchall()
            nos = [{'id_registro': nota_item['id_registro'], 'rotulo': nota_item['titulo']} for nota_item in notas]

            cursor_db.execute(, (id_usuario,))
            links = cursor_db.fetchall()
            arestas = [{'from': l['id_nota_origem'],
                        'to': l['id_nota_destino']} for l in links]
        except mysql.connector.Error as erro_bd:
            print(f"Erro ao buscar dados do grafo: {erro_bd}")
        finally:
            cursor_db.close()
            conexao_bd.close()

    return jsonify({'nos': nos, 'arestas': arestas})

@app.route('/notes<int:id_nota>flashcards')
@login_required
def view_flashcards(id_nota):
    flash('Funcionalidade de Flashcards ainda não implementada.', 'info')
    return redirect(url_for('view_note', id_nota=id_nota))

@app.route('/calendar')
@login_required
def view_calendar():
    flash('Funcionalidade de Calendário/Tarefas ainda não implementada.', 'info')
    return redirect(url_for('dashboard'))

@app.route('/api/flashcards', methods=['GET', 'POST'])
@login_required
def api_flashcards():
    id_usuario = session['id_usuario']
    conexao_bd = get_db_connection()

    if request.method == 'POST':
        dados = request.get_json()
        id_nota = dados.get('nota_id')
        conteudo_frente = dados.get('front_content')
        conteudo_verso = dados.get('back_content')

        if conexao_bd:
            try:
                cursor_db = conexao_bd.cursor_db()
                cursor_db.execute(
                    "INSERT INTO flashcards (nota_id, front_content, back_content) VALUES (%s, %s, %s)",
                    (id_nota, conteudo_frente, conteudo_verso)
                )
                conexao_bd.commit()
                id_flashcard = cursor_db.lastrowid
                return jsonify({'success': True, 'flashcard_id': id_flashcard})
            except mysql.connector.Error as erro_bd:
                return jsonify({'success': False, 'error': str(erro_bd)})
            finally:
                cursor_db.close()
                conexao_bd.close()

    else: 
        id_nota = request.args.get('nota_id')
        if conexao_bd:
            try:
                cursor_db = conexao_bd.cursor_db(dictionary=True)
                if id_nota:
                    cursor_db.execute(
                        "SELECT f.* FROM flashcards f JOIN notas nota_item ON f.nota_id = nota_item.id_registro WHERE nota_item.id_usuario = %s AND f.nota_id = %s",
                        (id_usuario, id_nota)
                    )
                else:
                    cursor_db.execute(
                        "SELECT f.* FROM flashcards f JOIN notas nota_item ON f.nota_id = nota_item.id_registro WHERE nota_item.id_usuario = %s",
                        (id_usuario,)
                    )
                flashcards = cursor_db.fetchall()
                return jsonify({'success': True, 'flashcards': flashcards})
            except mysql.connector.Error as erro_bd:
                return jsonify({'success': False, 'error': str(erro_bd)})
            finally:
                cursor_db.close()
                conexao_bd.close()

    return jsonify({'success': False, 'error': 'Erro de conexão com o banco de dados'})

@app.route('/api/tasks', methods=['GET', 'POST'])
@login_required
def api_tasks():
    id_usuario = session['id_usuario']
    conexao_bd = get_db_connection()

    if request.method == 'POST':
        dados = request.get_json()
        titulo = dados.get('titulo')
        descricao = dados.get('description', '')
        data_vencimento = dados.get('due_date')
        recorrente = dados.get('recurring', False)
        regra_recorrencia = dados.get('recurrence_rule', '')

        if conexao_bd:
            try:
                cursor_db = conexao_bd.cursor_db()
                cursor_db.execute(
                    "INSERT INTO tasks (id_usuario, titulo, description, due_date, recurring, recurrence_rule) VALUES (%s, %s, %s, %s, %s, %s)",
                    (id_usuario, titulo, descricao, data_vencimento, recorrente, regra_recorrencia)
                )
                conexao_bd.commit()
                id_tarefa = cursor_db.lastrowid
                return jsonify({'success': True, 'task_id': id_tarefa})
            except mysql.connector.Error as erro_bd:
                return jsonify({'success': False, 'error': str(erro_bd)})
            finally:
                cursor_db.close()
                conexao_bd.close()

    else: 
        if conexao_bd:
            try:
                cursor_db = conexao_bd.cursor_db(dictionary=True)
                cursor_db.execute(
                    "SELECT * FROM tasks WHERE id_usuario = %s ORDER BY due_date ASC",
                    (id_usuario,)
                )
                tarefas = cursor_db.fetchall()
                return jsonify({'success': True, 'tasks': tarefas})
            except mysql.connector.Error as erro_bd:
                return jsonify({'success': False, 'error': str(erro_bd)})
            finally:
                cursor_db.close()
                conexao_bd.close()

    return jsonify({'success': False, 'error': 'Erro de conexão com o banco de dados'})

@app.route('/api/tasks/<int:task_id>', methods=['PUT', 'DELETE'])
@login_required
def api_task_detail(task_id):
    id_usuario = session['id_usuario']
    conexao_bd = get_db_connection()

    if request.method == 'PUT':
        dados = request.get_json()
        concluida = dados.get('completed', False)

        if conexao_bd:
            try:
                cursor_db = conexao_bd.cursor_db()
                cursor_db.execute(
                    "UPDATE tasks SET completed = %s WHERE id_registro = %s AND id_usuario = %s",
                    (concluida, task_id, id_usuario)
                )
                conexao_bd.commit()
                return jsonify({'success': True})
            except mysql.connector.Error as erro_bd:
                return jsonify({'success': False, 'error': str(erro_bd)})
            finally:
                cursor_db.close()
                conexao_bd.close()

    elif request.method == 'DELETE':
        if conexao_bd:
            try:
                cursor_db = conexao_bd.cursor_db()
                cursor_db.execute(
                    "DELETE FROM tasks WHERE id_registro = %s AND id_usuario = %s",
                    (task_id, id_usuario)
                )
                conexao_bd.commit()
                return jsonify({'success': True})
            except mysql.connector.Error as erro_bd:
                return jsonify({'success': False, 'error': str(erro_bd)})
            finally:
                cursor_db.close()
                conexao_bd.close()

    return jsonify({'success': False, 'error': 'Erro de conexão com o banco de dados'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)