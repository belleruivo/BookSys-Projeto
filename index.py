from flask import Flask, render_template, request, redirect, session
import pymysql

app = Flask(__name__)

app.secret_key = 'eqwivcerldasdkjkgtirrewruywu'
db = pymysql.connect(host="localhost", user="root", password="", database="projetoflask")

@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        cursor = db.cursor()
        sql = "SELECT * FROM usuarios WHERE email = %s AND senha = %s"
        cursor.execute(sql, (email, senha))
        usuario = cursor.fetchone()
        
        if usuario:
            session['id'] = usuario[0]  # Armazena o ID do usuário na sessão
            return redirect("/home")
        else:
            return "Credenciais inválidas. Verifique seu email e senha e tente novamente."
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop('id', None)  # Remove o ID do usuário da sessão
    return redirect("/")

@app.route("/cadastro", methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        confirm_email = request.form.get('confirm_email')
        senha = request.form.get('senha')
        
        if email == confirm_email:
            cursor = db.cursor()
            sql = "INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)"
            cursor.execute(sql, (nome, email, senha))
            db.commit()
            return redirect("/")
        else:
            return "Os emails não correspondem!"
    
    return render_template("cadastro.html")

@app.route("/home", methods=['GET', 'POST'])
def home():
    if 'id' not in session:
        return redirect("/")
    
    if request.method == 'POST':
        id_livro = request.form.get('id_livro')
        titulo = request.form.get('titulo')
        isbn = request.form.get('isbn')
        autor = request.form.get('autor')
        genero = request.form.get('genero')
        descricao = request.form.get('descricao')
        
        cursor = db.cursor()
        if id_livro:
            sql = "UPDATE livros SET titulo = %s, isbn = %s, autor = %s, genero = %s, descricao = %s WHERE id_livro = %s"
            cursor.execute(sql, (titulo, isbn, autor, genero, descricao, id_livro))
        else:
            sql = "INSERT INTO livros (titulo, isbn, autor, genero, descricao) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (titulo, isbn, autor, genero, descricao))
        
        db.commit()

    cursor = db.cursor()
    sql = "SELECT * FROM livros"
    cursor.execute(sql)
    results = cursor.fetchall()
    return render_template("home.html", livros=results)

@app.route("/deletar_livro", methods=['GET'])
def deletar_livro():
    if 'id' not in session:
        return redirect("/")
    
    id_livro = request.args.get('id_livro')
    cursor = db.cursor()
    sql = "DELETE FROM livros WHERE id_livro = %s"
    cursor.execute(sql, (id_livro,))
    db.commit()
    return redirect("/home")

if __name__ == "__main__":
    app.run(debug=True)
