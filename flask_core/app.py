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
        conexao = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="zetria",
            port=3307,
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        return conexao
    except mysql.connector.Error as erro:
        print(f"Erro de conexão com o MySQL: {erro}")
        flash(f"Erro crítico de conexão com o banco de dados: {erro}", "danger")
        return None

def login_required(funcao):
    @wraps(funcao)
    def funcao_decorada(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa fazer login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return funcao(*args, **kwargs)
    return funcao_decorada

def extract_links(conteudo):
    return re.findall(r"\[\[([^\]]+)\]\]", conteudo)

def extract_tags(conteudo):
    return re.findall(r"(?:\s|^)#([a-zA-Z0-9_\-]+)(?:\s|$)", conteudo)

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome_usuario = request.form['username']
        senha = request.form['password']
        confirmar_senha = request.form.get('confirm_password', '')
        
        if senha != confirmar_senha:
            flash('As senhas não coincidem.', 'danger')
            return render_template('Cadastro.html')
            
        senha_hash = generate_password_hash(senha)
        conexao = get_db_connection()
        cursor = None
        if conexao:
            try:
                cursor = conexao.cursor()
                cursor.execute(
                    "INSERT INTO usuarios (username, password_hash) VALUES (%s, %s)", (nome_usuario, senha_hash))
                conexao.commit()
                flash('Usuário registrado com sucesso! Faça o login.', 'success')
                return redirect(url_for('login'))
            except mysql.connector.IntegrityError:
                flash('Nome de usuário já existe.', 'danger')
            except mysql.connector.Error as erro:
                flash(f"Erro ao registrar: {erro}", 'danger')
            finally:
                if cursor:
                    cursor.close()
                conexao.close()
        else:
            flash('Erro ao conectar ao banco de dados.', 'danger')

    return render_template('Cadastro.html')

@app.route('/interface')
@login_required
def interface():
    return render_template('interface.html', username=session['username'])

@app.route('/notas')
@login_required
def notas():
    return render_template('Interface.notas.html', username=session['username'])

@app.route('/nota')
@login_required
def nota():
    return render_template('nota.html', username=session['username'])

@app.route('/flashcards')
@login_required
def flashcards():
    return render_template('interface.flashcard1.html', username=session['username'])

@app.route('/flashcards2')
@login_required
def flashcards2():
    return render_template('interface.flashcard2.html', username=session['username'])

@app.route('/flashcards3')
@login_required
def flashcards3():
    return render_template('interface.flashcard3.html', username=session['username'])

@app.route('/calendario')
@login_required
def calendario():
    return render_template('calendario.html', username=session['username'])

@app.route('/grafos')
@login_required
def grafos():
    return render_template('grafos.html', username=session['username'])

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome_usuario = request.form['username']
        senha = request.form['password']
        senha_hash = generate_password_hash(senha)
        conexao = get_db_connection()
        cursor = None
        if conexao:
            try:
                cursor = conexao.cursor()
                cursor.execute(
                    "INSERT INTO usuarios (username, password_hash) VALUES (%s, %s)", (nome_usuario, senha_hash))
                conexao.commit()
                flash('Usuário registrado com sucesso! Faça o login.', 'success')
                return redirect(url_for('login'))
            except mysql.connector.IntegrityError:
                flash('Nome de usuário já existe.', 'danger')
            except mysql.connector.Error as erro:
                flash(f"Erro ao registrar: {erro}", 'danger')
            finally:
                if cursor:
                    cursor.close()
                conexao.close()
        else:
            flash('Erro ao conectar ao banco de dados.', 'danger')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nome_usuario = request.form['username']
        senha = request.form['password']
        conexao = get_db_connection()
        cursor = None
        if conexao:
            try:
                cursor = conexao.cursor(dictionary=True)
                cursor.execute(
                    "SELECT * FROM usuarios WHERE username = %s", (nome_usuario,))
                usuario = cursor.fetchone()
                if usuario and check_password_hash(usuario['password_hash'], senha):
                    session['user_id'] = usuario['id']
                    session['username'] = usuario['username']
                    flash('Login bem-sucedido!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Nome de usuário ou senha inválidos.', 'danger')
            except mysql.connector.Error as erro:
                flash(f"Erro ao fazer login: {erro}", 'danger')
            finally:
                if cursor:
                    cursor.close()
                conexao.close()
        else:
            flash('Erro ao conectar ao banco de dados.', 'danger')

    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    id_usuario = session['user_id']
    conexao = get_db_connection()
    notas = []
    if conexao:
        cursor = conexao.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT id, title, 
                SUBSTRING(REGEXP_REPLACE(content, '<[^>]*>', ''), 1, 150) as snippet, 
                updated_at FROM notas 
                WHERE user_id = %s 
                ORDER BY updated_at DESC
            """, (id_usuario,))
            notas = cursor.fetchall()
        except mysql.connector.Error as erro:
            flash(f"Erro ao buscar notas: {erro}", "danger")
        finally:
            cursor.close()
            conexao.close()

    return render_template('dashboard.html', username=session['username'], notes=notas)

def process_note_links_tags(conexao, cursor, id_nota, conteudo):
    id_usuario = session['user_id']
    titulos_notas_linkadas = extract_links(conteudo)
    ids_notas_destino = []
    if titulos_notas_linkadas:
        strings_formato = ','.join(['%s'] * len(titulos_notas_linkadas))
        consulta = f"SELECT id FROM notas WHERE user_id = %s AND title IN ({strings_formato})"
        parametros = [id_usuario] + titulos_notas_linkadas
        cursor.execute(consulta, parametros)
        notas_destino = cursor.fetchall()
        ids_notas_destino = [nota[0] for nota in notas_destino]

    cursor.execute(
        "DELETE FROM links_notas WHERE source_nota_id = %s", (id_nota,))
    if ids_notas_destino:
        dados_link = [(id_nota, id_destino)
                      for id_destino in ids_notas_destino if id_destino != id_nota]
        if dados_link:
            cursor.executemany(
                "INSERT IGNORE INTO links_notas (source_nota_id, target_nota_id) VALUES (%s, %s)", dados_link)

    nomes_tags = list(set(extract_tags(conteudo)))
    ids_tags = []
    for nome_tag in nomes_tags:
        cursor.execute(
            "INSERT IGNORE INTO tags (name) VALUES (%s)", (nome_tag,))
        cursor.execute("SELECT id FROM tags WHERE name = %s", (nome_tag,))
        resultado_id_tag = cursor.fetchone()
        if resultado_id_tag:
            ids_tags.append(resultado_id_tag[0])

    cursor.execute("DELETE FROM nota_tags WHERE nota_id = %s", (id_nota,))
    if ids_tags:
        dados_link_tags = [(id_nota, id_tag) for id_tag in ids_tags]
        cursor.executemany(
            "INSERT IGNORE INTO nota_tags (nota_id, tag_id) VALUES (%s, %s)", dados_link_tags)

@app.route('/notessave', methods=['POST'])
@login_required
def save_note():
    id_usuario = session['user_id']
    titulo = request.form['title']
    conteudo = request.form['content']
    conexao = get_db_connection()
    cursor = None
    if conexao:
        try:
            cursor = conexao.cursor()
            cursor.execute(
                "INSERT INTO notas (user_id, title, content) VALUES (%s, %s, %s)", (id_usuario, titulo, conteudo))
            id_nota = cursor.lastrowid
            process_note_links_tags(conexao, cursor, id_nota, conteudo)
            conexao.commit()
            flash('Nota salva com sucesso!', 'success')
        except mysql.connector.Error as erro:
            flash(f"Erro ao salvar nota: {erro}", "danger")
            conexao.rollback()
        finally:
            cursor.close()
            conexao.close()
    else:
        flash('Erro ao conectar ao banco de dados para salvar nota.', 'danger')

    return redirect(url_for('dashboard'))

@app.route('/notes<int:note_id>')
@login_required
def view_note(note_id):
    id_usuario = session['user_id']
    conexao = get_db_connection()
    nota, tags, notas_linkadas, notas_que_linkam = None, [], [], []
    if conexao:
        cursor = conexao.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT * FROM notas WHERE id = %s AND user_id = %s", (note_id, id_usuario))
            nota = cursor.fetchone()
            if not nota:
                flash('Nota não encontrada ou acesso não permitido.', 'warning')
                return redirect(url_for('dashboard'))

            cursor.execute(
                "SELECT t.name FROM tags t JOIN nota_tags nt ON t.id = nt.tag_id WHERE nt.nota_id = %s", (note_id,))
            tags = [linha['name'] for linha in cursor.fetchall()]

            cursor.execute(
                "SELECT n.id, n.title FROM notas n JOIN links_notas ln ON n.id = ln.target_nota_id WHERE ln.source_nota_id = %s", (note_id,))
            notas_linkadas = cursor.fetchall()

            cursor.execute(
                "SELECT n.id, n.title FROM notas n JOIN links_notas ln ON n.id = ln.source_nota_id WHERE ln.target_nota_id = %s", (note_id,))
            notas_que_linkam = cursor.fetchall()
        except mysql.connector.Error as erro:
            flash(f"Erro ao buscar detalhes da nota: {erro}", "danger")
        finally:
            cursor.close()
            conexao.close()
    else:
        flash('Erro ao conectar ao banco de dados.', 'danger')

    return render_template('view_note.html', note=nota, tags=tags, linked_notes=notas_linkadas, linking_notes=notas_que_linkam)

@app.route('/notesedit<int:note_id>', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    id_usuario = session['user_id']
    conexao = get_db_connection()
    if not conexao:
        flash('Erro ao conectar ao banco de dados.', 'danger')
        return redirect(url_for('dashboard'))

    cursor = conexao.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM notas WHERE id = %s AND user_id = %s", (note_id, id_usuario))
        nota = cursor.fetchone()
        if not nota:
            flash('Nota não encontrada ou acesso não permitido.', 'warning')
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            titulo = request.form['title']
            conteudo = request.form['content']
            cursor.execute(
                "UPDATE notas SET title = %s, content = %s WHERE id = %s", (titulo, conteudo, note_id))
            process_note_links_tags(conexao, cursor, note_id, conteudo)
            conexao.commit()
            flash('Nota atualizada com sucesso!', 'success')
            return redirect(url_for('view_note', note_id=note_id))
    except mysql.connector.Error as erro:
        flash(f"Erro ao editar nota: {erro}", "danger")
        conexao.rollback()
    finally:
        cursor.close()
        conexao.close()

    return render_template('edit_note.html', note=nota)

@app.route('/notesdelete<int:note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    id_usuario = session['user_id']
    conexao = get_db_connection()
    if not conexao:
        flash('Erro ao conectar ao banco de dados.', 'danger')
        return redirect(url_for('dashboard'))

    cursor = conexao.cursor()
    try:
        cursor.execute(
            "DELETE FROM notas WHERE id = %s AND user_id = %s", (note_id, id_usuario))
        conexao.commit()
        if cursor.rowcount > 0:
            flash('Nota excluída com sucesso!', 'success')
        else:
            flash('Nota não encontrada ou acesso não permitido.', 'warning')
    except mysql.connector.Error as erro:
        flash(f"Erro ao excluir nota: {erro}", "danger")
        conexao.rollback()
    finally:
        cursor.close()
        conexao.close()

    return redirect(url_for('dashboard'))

@app.route('/search')
@login_required
def search_notes():
    id_usuario = session['user_id']
    consulta = request.args.get('q', '/')
    resultados = []
    conexao = get_db_connection()
    if conexao and consulta:
        try:
            cursor = conexao.cursor(dictionary=True)
            termo_busca = f"%{consulta}%"
            sql = """
                SELECT DISTINCT n.id, n.title, 
                SUBSTRING(REGEXP_REPLACE(n.content, '<[^>]*>', ''), 1, 150) as snippet, n.updated_at
                FROM notas n
                LEFT JOIN nota_tags nt ON n.id = nt.nota_id
                LEFT JOIN tags t ON nt.tag_id = t.id
                WHERE n.user_id = %s AND (
                    n.title LIKE %s OR n.content LIKE %s OR t.name = %s
                )
                ORDER BY n.updated_at DESC
            """
            cursor.execute(sql, (id_usuario, termo_busca, termo_busca, consulta))
            resultados = cursor.fetchall()
        except mysql.connector.Error as erro:
            flash(f"Erro ao buscar notas: {erro}", "danger")
        finally:
            cursor.close()
            conexao.close()

    return render_template('search_results.html', query=consulta, results=resultados)

@app.route('/graph')
@login_required
def view_graph():
    return render_template('graph.html')

@app.route('/graph_data')
@login_required
def graph_data():
    id_usuario = session['user_id']
    nos, arestas = [], []
    conexao = get_db_connection()
    if conexao:
        try:
            cursor = conexao.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, title FROM notas WHERE user_id = %s", (id_usuario,))
            notas = cursor.fetchall()
            nos = [{'id': n['id'], 'label': n['title']} for n in notas]

            cursor.execute("""
                SELECT ln.source_nota_id, ln.target_nota_id
                FROM links_notas ln
                JOIN notas n ON ln.source_nota_id = n.id
                WHERE n.user_id = %s
            """, (id_usuario,))
            links = cursor.fetchall()
            arestas = [{'from': l['source_nota_id'],
                        'to': l['target_nota_id']} for l in links]
        except mysql.connector.Error as erro:
            print(f"Erro ao buscar dados do grafo: {erro}")
        finally:
            cursor.close()
            conexao.close()

    return jsonify({'nodes': nos, 'edges': arestas})

@app.route('/notes<int:note_id>flashcards')
@login_required
def view_flashcards(note_id):
    flash('Funcionalidade de Flashcards ainda não implementada.', 'info')
    return redirect(url_for('view_note', note_id=note_id))

@app.route('/calendar')
@login_required
def view_calendar():
    flash('Funcionalidade de Calendário/Tarefas ainda não implementada.', 'info')
    return redirect(url_for('dashboard'))

@app.route('/api/flashcards', methods=['GET', 'POST'])
@login_required
def api_flashcards():
    id_usuario = session['user_id']
    conexao = get_db_connection()
    
    if request.method == 'POST':
        dados = request.get_json()
        id_nota = dados.get('nota_id')
        conteudo_frente = dados.get('front_content')
        conteudo_verso = dados.get('back_content')
        
        if conexao:
            try:
                cursor = conexao.cursor()
                cursor.execute(
                    "INSERT INTO flashcards (nota_id, front_content, back_content) VALUES (%s, %s, %s)",
                    (id_nota, conteudo_frente, conteudo_verso)
                )
                conexao.commit()
                id_flashcard = cursor.lastrowid
                return jsonify({'success': True, 'flashcard_id': id_flashcard})
            except mysql.connector.Error as erro:
                return jsonify({'success': False, 'error': str(erro)})
            finally:
                cursor.close()
                conexao.close()
        
    else: 
        id_nota = request.args.get('nota_id')
        if conexao:
            try:
                cursor = conexao.cursor(dictionary=True)
                if id_nota:
                    cursor.execute(
                        "SELECT f.* FROM flashcards f JOIN notas n ON f.nota_id = n.id WHERE n.user_id = %s AND f.nota_id = %s",
                        (id_usuario, id_nota)
                    )
                else:
                    cursor.execute(
                        "SELECT f.* FROM flashcards f JOIN notas n ON f.nota_id = n.id WHERE n.user_id = %s",
                        (id_usuario,)
                    )
                flashcards = cursor.fetchall()
                return jsonify({'success': True, 'flashcards': flashcards})
            except mysql.connector.Error as erro:
                return jsonify({'success': False, 'error': str(erro)})
            finally:
                cursor.close()
                conexao.close()
    
    return jsonify({'success': False, 'error': 'Erro de conexão com o banco de dados'})

@app.route('/api/tasks', methods=['GET', 'POST'])
@login_required
def api_tasks():
    id_usuario = session['user_id']
    conexao = get_db_connection()
    
    if request.method == 'POST':
        dados = request.get_json()
        titulo = dados.get('title')
        descricao = dados.get('description', '')
        data_vencimento = dados.get('due_date')
        recorrente = dados.get('recurring', False)
        regra_recorrencia = dados.get('recurrence_rule', '')
        
        if conexao:
            try:
                cursor = conexao.cursor()
                cursor.execute(
                    "INSERT INTO tasks (user_id, title, description, due_date, recurring, recurrence_rule) VALUES (%s, %s, %s, %s, %s, %s)",
                    (id_usuario, titulo, descricao, data_vencimento, recorrente, regra_recorrencia)
                )
                conexao.commit()
                id_tarefa = cursor.lastrowid
                return jsonify({'success': True, 'task_id': id_tarefa})
            except mysql.connector.Error as erro:
                return jsonify({'success': False, 'error': str(erro)})
            finally:
                cursor.close()
                conexao.close()
        
    else: 
        if conexao:
            try:
                cursor = conexao.cursor(dictionary=True)
                cursor.execute(
                    "SELECT * FROM tasks WHERE user_id = %s ORDER BY due_date ASC",
                    (id_usuario,)
                )
                tarefas = cursor.fetchall()
                return jsonify({'success': True, 'tasks': tarefas})
            except mysql.connector.Error as erro:
                return jsonify({'success': False, 'error': str(erro)})
            finally:
                cursor.close()
                conexao.close()
    
    return jsonify({'success': False, 'error': 'Erro de conexão com o banco de dados'})

@app.route('/api/tasks/<int:task_id>', methods=['PUT', 'DELETE'])
@login_required
def api_task_detail(task_id):
    id_usuario = session['user_id']
    conexao = get_db_connection()
    
    if request.method == 'PUT':
        dados = request.get_json()
        concluida = dados.get('completed', False)
        
        if conexao:
            try:
                cursor = conexao.cursor()
                cursor.execute(
                    "UPDATE tasks SET completed = %s WHERE id = %s AND user_id = %s",
                    (concluida, task_id, id_usuario)
                )
                conexao.commit()
                return jsonify({'success': True})
            except mysql.connector.Error as erro:
                return jsonify({'success': False, 'error': str(erro)})
            finally:
                cursor.close()
                conexao.close()
        
    elif request.method == 'DELETE':
        if conexao:
            try:
                cursor = conexao.cursor()
                cursor.execute(
                    "DELETE FROM tasks WHERE id = %s AND user_id = %s",
                    (task_id, id_usuario)
                )
                conexao.commit()
                return jsonify({'success': True})
            except mysql.connector.Error as erro:
                return jsonify({'success': False, 'error': str(erro)})
            finally:
                cursor.close()
                conexao.close()
    
    return jsonify({'success': False, 'error': 'Erro de conexão com o banco de dados'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)