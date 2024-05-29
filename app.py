from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Function to establish connection with SQLite database
def get_db_connection():
    conn = sqlite3.connect('docker.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    schema = """
    DROP TABLE IF EXISTS items;
    CREATE TABLE items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        price REAL,  -- Ajout du champ price
        user_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    );
    """
    conn.executescript(schema)
    conn.commit()
    conn.close()


# Initialize the database
init_db()


# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hash_password(password)
        conn = get_db_connection()
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                     (username, hashed_password))
        conn.commit()
        conn.close()
        flash('Inscription réussi. Veuillez vous connecter.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hash_password(password)
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_password)).fetchone()
        conn.close()
        if user:
            session['logged_in'] = True
            session['username'] = user['username']
            session['user_id'] = user['id']  # Ensure user_id is set
            flash('Connexion réussie.', 'success')
            return redirect(url_for('home'))
        else:
            flash("Nom d'utilisateur ou mot de passe invalide. Veuillez réessayer.", 'error')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()  # Clear the entire session
    flash('Vous avez été déconnecté.', 'success')
    return redirect(url_for('index'))


@app.route('/home')
def home():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))
    username = session.get('username')
    return render_template('home.html', username=username)


@app.route('/')
def index():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))
    if 'user_id' not in session:
        flash('User ID not found in session.', 'error')
        return redirect(url_for('logout'))
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items WHERE user_id = ?', (session['user_id'],)).fetchall()
    conn.close()
    username = session.get('username')
    return render_template('index.html', items=items, username=username)




@app.route('/add', methods=['GET', 'POST'])
def add_item():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))
    if request.method == 'POST':
        conn = get_db_connection()
        conn.execute('INSERT INTO items (title, description, price, user_id) VALUES (?, ?, ?, ?)',
                     (request.form['title'], request.form['description'], request.form['price'], session['user_id']))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add.html')


@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM items WHERE id = ? AND user_id = ?', (item_id, session['user_id'])).fetchone()
    if item is None:
        flash('Item not found or you do not have permission to edit this item.', 'error')
        return redirect(url_for('index'))
    if request.method == 'POST':
        conn.execute('UPDATE items SET title = ?, description = ?, price = ? WHERE id = ? AND user_id = ?',
                     (request.form['title'], request.form['description'], request.form['price'], item_id, session['user_id']))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('edit.html', item=item)



@app.route('/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('DELETE FROM items WHERE id = ? AND user_id = ?', (item_id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
