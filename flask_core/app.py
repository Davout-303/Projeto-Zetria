import os
import re
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)


def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="zetria_user",
            password="password",
            database="zetria",
            port=3307,
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Erro de conexão com o MySQL: {err}")
        flash(f"Erro crítico de conexão com o banco de dados: {err}", "danger")
        return None


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa fazer login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def extract_links(content):
    return re.findall(r"\[\[([^\]]+)\]\]", content)


def extract_tags(content):
    return re.findall(r"(?:\s|^)#([a-zA-Z0-9_\-]+)(?:\s|$)", content)


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        conn = get_db_connection()
        cursor = None
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO usuarios (username, password_hash) VALUES (%s, %s)", (username, hashed_password))
                conn.commit()
                flash('Usuário registrado com sucesso! Faça o login.', 'success')
                return redirect(url_for('login'))
            except mysql.connector.IntegrityError:
                flash('Nome de usuário já existe.', 'danger')
            except mysql.connector.Error as err:
                flash(f"Erro ao registrar: {err}", 'danger')
            finally:
                if cursor:
                    cursor.close()
                conn.close()
        else:
            flash('Erro ao conectar ao banco de dados.', 'danger')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = None
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(
                    "SELECT * FROM usuarios WHERE username = %s", (username,))
                user = cursor.fetchone()
                if user and check_password_hash(user['password_hash'], password):
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    flash('Login bem-sucedido!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Nome de usuário ou senha inválidos.', 'danger')
            except mysql.connector.Error as err:
                flash(f"Erro ao fazer login: {err}", 'danger')
            finally:
                if cursor:
                    cursor.close()
                conn.close()
        else:
            flash('Erro ao conectar ao banco de dados.', 'danger')

    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('Login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    conn = get_db_connection()
    notes = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT id, title, 
                SUBSTRING(REGEXP_REPLACE(content, '<[^>]*>', ''), 1, 150) as snippet, 
                updated_at FROM notas 
                WHERE user_id = %s 
                ORDER BY updated_at DESC
            """, (user_id,))
            notes = cursor.fetchall()
        except mysql.connector.Error as err:
            flash(f"Erro ao buscar notas: {err}", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template('dashboard.html', username=session['username'], notes=notes)


def process_note_links_tags(conn, cursor, note_id, content):
    user_id = session['user_id']
    linked_note_titles = extract_links(content)
    target_note_ids = []
    if linked_note_titles:
        format_strings = ','.join(['%s'] * len(linked_note_titles))
        query = f"SELECT id FROM notas WHERE user_id = %s AND title IN ({format_strings})"
        params = [user_id] + linked_note_titles
        cursor.execute(query, params)
        target_notes = cursor.fetchall()
        target_note_ids = [note[0] for note in target_notes]

    cursor.execute(
        "DELETE FROM links_notas WHERE source_nota_id = %s", (note_id,))
    if target_note_ids:
        link_data = [(note_id, target_id)
                     for target_id in target_note_ids if target_id != note_id]
        if link_data:
            cursor.executemany(
                "INSERT IGNORE INTO links_notas (source_nota_id, target_nota_id) VALUES (%s, %s)", link_data)

    tag_names = list(set(extract_tags(content)))
    tag_ids = []
    for tag_name in tag_names:
        cursor.execute(
            "INSERT IGNORE INTO tags (name) VALUES (%s)", (tag_name,))
        cursor.execute("SELECT id FROM tags WHERE name = %s", (tag_name,))
        tag_id_result = cursor.fetchone()
        if tag_id_result:
            tag_ids.append(tag_id_result[0])

    cursor.execute("DELETE FROM nota_tags WHERE nota_id = %s", (note_id,))
    if tag_ids:
        tag_link_data = [(note_id, tag_id) for tag_id in tag_ids]
        cursor.executemany(
            "INSERT IGNORE INTO nota_tags (nota_id, tag_id) VALUES (%s, %s)", tag_link_data)


@app.route('/notessave', methods=['POST'])
@login_required
def save_note():
    user_id = session['user_id']
    title = request.form['title']
    content = request.form['content']
    conn = get_db_connection()
    cursor = None
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO notas (user_id, title, content) VALUES (%s, %s, %s)", (user_id, title, content))
            note_id = cursor.lastrowid
            process_note_links_tags(conn, cursor, note_id, content)
            conn.commit()
            flash('Nota salva com sucesso!', 'success')
        except mysql.connector.Error as err:
            flash(f"Erro ao salvar nota: {err}", "danger")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    else:
        flash('Erro ao conectar ao banco de dados para salvar nota.', 'danger')

    return redirect(url_for('dashboard'))


@app.route('/notes<int:note_id>')
@login_required
def view_note(note_id):
    user_id = session['user_id']
    conn = get_db_connection()
    note, tags, linked_notes, linking_notes = None, [], [], []
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT * FROM notas WHERE id = %s AND user_id = %s", (note_id, user_id))
            note = cursor.fetchone()
            if not note:
                flash('Nota não encontrada ou acesso não permitido.', 'warning')
                return redirect(url_for('dashboard'))

            cursor.execute(
                "SELECT t.name FROM tags t JOIN nota_tags nt ON t.id = nt.tag_id WHERE nt.nota_id = %s", (note_id,))
            tags = [row['name'] for row in cursor.fetchall()]

            cursor.execute(
                "SELECT n.id, n.title FROM notas n JOIN links_notas ln ON n.id = ln.target_nota_id WHERE ln.source_nota_id = %s", (note_id,))
            linked_notes = cursor.fetchall()

            cursor.execute(
                "SELECT n.id, n.title FROM notas n JOIN links_notas ln ON n.id = ln.source_nota_id WHERE ln.target_nota_id = %s", (note_id,))
            linking_notes = cursor.fetchall()
        except mysql.connector.Error as err:
            flash(f"Erro ao buscar detalhes da nota: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
    else:
        flash('Erro ao conectar ao banco de dados.', 'danger')

    return render_template('view_note.html', note=note, tags=tags, linked_notes=linked_notes, linking_notes=linking_notes)


@app.route('/notesedit<int:note_id>', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    user_id = session['user_id']
    conn = get_db_connection()
    if not conn:
        flash('Erro ao conectar ao banco de dados.', 'danger')
        return redirect(url_for('dashboard'))

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM notas WHERE id = %s AND user_id = %s", (note_id, user_id))
        note = cursor.fetchone()
        if not note:
            flash('Nota não encontrada ou acesso não permitido.', 'warning')
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            cursor.execute(
                "UPDATE notas SET title = %s, content = %s WHERE id = %s", (title, content, note_id))
            process_note_links_tags(conn, cursor, note_id, content)
            conn.commit()
            flash('Nota atualizada com sucesso!', 'success')
            return redirect(url_for('view_note', note_id=note_id))
    except mysql.connector.Error as err:
        flash(f"Erro ao editar nota: {err}", "danger")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

    return render_template('edit_note.html', note=note)


@app.route('/notesdelete<int:note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    user_id = session['user_id']
    conn = get_db_connection()
    if not conn:
        flash('Erro ao conectar ao banco de dados.', 'danger')
        return redirect(url_for('dashboard'))

    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM notas WHERE id = %s AND user_id = %s", (note_id, user_id))
        conn.commit()
        if cursor.rowcount > 0:
            flash('Nota excluída com sucesso!', 'success')
        else:
            flash('Nota não encontrada ou acesso não permitido.', 'warning')
    except mysql.connector.Error as err:
        flash(f"Erro ao excluir nota: {err}", "danger")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('dashboard'))


@app.route('/search')
@login_required
def search_notes():
    user_id = session['user_id']
    query = request.args.get('q', '/')
    results = []
    conn = get_db_connection()
    if conn and query:
        try:
            cursor = conn.cursor(dictionary=True)
            search_term = f"%{query}%"
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
            cursor.execute(sql, (user_id, search_term, search_term, query))
            results = cursor.fetchall()
        except mysql.connector.Error as err:
            flash(f"Erro ao buscar notas: {err}", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template('search_results.html', query=query, results=results)


@app.route('/graph')
@login_required
def view_graph():
    return render_template('graph.html')


@app.route('/graph_data')
@login_required
def graph_data():
    user_id = session['user_id']
    nodes, edges = [], []
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, title FROM notas WHERE user_id = %s", (user_id,))
            notes = cursor.fetchall()
            nodes = [{'id': n['id'], 'label': n['title']} for n in notes]

            cursor.execute("""
                SELECT ln.source_nota_id, ln.target_nota_id
                FROM links_notas ln
                JOIN notas n ON ln.source_nota_id = n.id
                WHERE n.user_id = %s
            """, (user_id,))
            links = cursor.fetchall()
            edges = [{'from': l['source_nota_id'],
                      'to': l['target_nota_id']} for l in links]
        except mysql.connector.Error as err:
            print(f"Erro ao buscar dados do grafo: {err}")
        finally:
            cursor.close()
            conn.close()

    return jsonify({'nodes': nodes, 'edges': edges})


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
