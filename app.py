import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, g

app = Flask(__name__)

DATABASE = 'todos.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
    print("Database initialized successfully")

def db_exists():
    return os.path.exists(DATABASE)

def check_table_exists():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='todos'")
        table_exists = cursor.fetchone() is not None
        print(f"'todos' table exists: {table_exists}")
        return table_exists

@app.route('/')
def index():
    db = get_db()
    cur = db.execute('SELECT id, task, completed FROM todos')
    todos = cur.fetchall()
    return render_template('index.html', todos=todos)

@app.route('/add', methods=['POST'])
def add_todo():
    task = request.form['task']
    if task:
        db = get_db()
        db.execute('INSERT INTO todos (task) VALUES (?)', [task])
        db.commit()
    return redirect(url_for('index'))

@app.route('/complete/<int:id>')
def complete_todo(id):
    db = get_db()
    db.execute('UPDATE todos SET completed = 1 WHERE id = ?', [id])
    db.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_todo(id):
    db = get_db()
    db.execute('DELETE FROM todos WHERE id = ?', [id])
    db.commit()
    return redirect(url_for('index'))

def initialize_app():
    with app.app_context():
        if not db_exists():
            print("Database file does not exist. Creating...")
            init_db()
        else:
            print("Database file exists.")
        
        if not check_table_exists():
            print("Table 'todos' does not exist. Initializing database...")
            init_db()

if __name__ == '__main__':
    initialize_app()
    app.run(debug=True)