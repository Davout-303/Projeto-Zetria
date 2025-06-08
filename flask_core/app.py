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
            user="notewise_user",
            password="root",
            database="schema.sql",
            port=3307,
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Erro de conexão com o MySQL: {err}")
        flash(f"Erro crítico de conexão com o banco de dados: {err}", "danger")
        return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        email = request.form['email']
        password_input = request.form['password'].encode('utf-8')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE email = %s', (email,))
        account = cursor.fetchone()
        cursor.close()
        if account and bcrypt.checkpw(password_input, account['password'].encode('utf-8')):
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('dashboard'))
        else:
            msg = 'Email ou senha incorretos!'
    return render_template('login.html', msg=msg)

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE email = %s', (email,))
        account = cursor.fetchone()
        if account:
            msg = 'Conta já existe!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Endereço de email inválido!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Nome de usuário deve conter apenas letras e números!'
        elif not username or not password or not email:
            msg = 'Por favor, preencha o formulário!'
        else:
            hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
            cursor.execute('INSERT INTO accounts (username, email, password) VALUES (%s, %s, %s)', (username, email, hashed_password.decode('utf-8')))
            mysql.connection.commit()
            msg = 'Você se registrou com sucesso!'
            return redirect(url_for('login'))
    return render_template('register.html', msg=msg)

@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        return render_template('dashboard.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
