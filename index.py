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

@app.route("/home")
def home():
    if 'id' not in session:
        return redirect("/")
    return render_template("home.html")

@app.route("/livros", methods=['GET', 'POST'])
def livros():
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
            # Atualiza o livro existente
            sql = "UPDATE livros SET titulo = %s, isbn = %s, autor = %s, genero = %s, descricao = %s WHERE id_livro = %s"
            cursor.execute(sql, (titulo, isbn, autor, genero, descricao, id_livro))
        else:
            # Verifica se o livro já existe antes de inserir
            cursor.execute('SELECT COUNT(*) FROM livros WHERE isbn = %s', (isbn,))
            if cursor.fetchone()[0] == 0:
                sql = "INSERT INTO livros (titulo, isbn, autor, genero, descricao, disponivel) VALUES (%s, %s, %s, %s, %s, 1)"
                cursor.execute(sql, (titulo, isbn, autor, genero, descricao))
            else:
                return redirect("/livros")  # Evita duplicação

        db.commit()

    cursor = db.cursor()
    sql = "SELECT * FROM livros WHERE disponivel = 1"
    cursor.execute(sql)
    results = cursor.fetchall()
    return render_template("livros.html", livros=results)

@app.route("/deletar_livro", methods=['GET'])
def deletar_livro():
    if 'id' not in session:
        return redirect("/")
    
    id_livro = request.args.get('id_livro')
    cursor = db.cursor()
    sql = "DELETE FROM livros WHERE id_livro = %s"
    cursor.execute(sql, (id_livro,))
    db.commit()
    return redirect("/livros")

@app.route("/emprestimos", methods=['GET', 'POST'])
def emprestimos():
    if 'id' not in session:
        return redirect("/")
    
    if request.method == 'POST':
        nome_usuario = request.form.get('nome_usuario')
        id_livro = request.form.get('id_livro')
        data_emprestimo = request.form.get('data_emprestimo')
        data_devolucao = request.form.get('data_devolucao')

        if nome_usuario and id_livro and data_emprestimo and data_devolucao:
            cursor = db.cursor()
            
            # Adiciona um novo empréstimo
            sql = """INSERT INTO emprestimos (nome_usuario, id_livro, data_emprestimo, data_devolucao)
                     VALUES (%s, %s, %s, %s)"""
            cursor.execute(sql, (nome_usuario, id_livro, data_emprestimo, data_devolucao))
            db.commit()
            
            # Atualiza a disponibilidade do livro
            cursor.execute("UPDATE livros SET disponivel = 0 WHERE id_livro = %s", (id_livro,))
            db.commit()
        else:
            return "Todos os campos são obrigatórios!"

    cursor = db.cursor()
    # Consulta modificada para incluir o nome do livro
    sql = """SELECT emprestimos.id_emprestimo, emprestimos.nome_usuario, livros.titulo, emprestimos.data_emprestimo, emprestimos.data_devolucao
             FROM emprestimos
             JOIN livros ON emprestimos.id_livro = livros.id_livro"""
    cursor.execute(sql)
    emprestimos = cursor.fetchall()

    cursor.execute("SELECT * FROM livros WHERE disponivel = 1")
    livros_disponiveis = cursor.fetchall()

    return render_template("emprestimos.html", emprestimos=emprestimos, livros=livros_disponiveis)

@app.route("/editar_emprestimo", methods=['POST'])
def editar_emprestimo():
    if 'id' not in session:
        return redirect("/")
    
    id_emprestimo = request.form.get('id_emprestimo')
    nome_usuario = request.form.get('nome_usuario')
    id_livro = request.form.get('id_livro')
    data_emprestimo = request.form.get('data_emprestimo')
    data_devolucao = request.form.get('data_devolucao')
    
    cursor = db.cursor()
    sql = """UPDATE emprestimos
             SET nome_usuario = %s, id_livro = %s, data_emprestimo = %s, data_devolucao = %s
             WHERE id_emprestimo = %s"""
    cursor.execute(sql, (nome_usuario, id_livro, data_emprestimo, data_devolucao, id_emprestimo))
    db.commit()
    
    return redirect("/emprestimos")

@app.route("/confirmar_devolucao", methods=['GET'])
def confirmar_devolucao():
    if 'id' not in session:
        return redirect("/")
    
    id_emprestimo = request.args.get('id_emprestimo')
    
    cursor = db.cursor()
    cursor.execute("SELECT id_livro FROM emprestimos WHERE id_emprestimo = %s", (id_emprestimo,))
    id_livro = cursor.fetchone()[0]
    
    # Remove o empréstimo
    cursor.execute("DELETE FROM emprestimos WHERE id_emprestimo = %s", (id_emprestimo,))
    db.commit()
    
    # Atualiza a disponibilidade do livro
    cursor.execute("UPDATE livros SET disponivel = 1 WHERE id_livro = %s", (id_livro,))
    db.commit()
    
    return redirect("/emprestimos")

if __name__ == "__main__":
    app.run(debug=True)
