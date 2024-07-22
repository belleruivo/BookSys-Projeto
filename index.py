from flask import Flask, render_template, request, redirect, session
import datetime
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
    return render_template("home.html", show_navbar = True)

@app.route("/livros", methods=['GET', 'POST'])
def livros():
    if 'id' not in session:
        return redirect("/")

    # Lógica para tratamento de POST (Cadastro e Edição de Livros)
    if request.method == 'POST':
        id_livro = request.form.get('id_livro')
        titulo = request.form.get('titulo')
        isbn = request.form.get('isbn')
        autor = request.form.get('autor')
        genero = request.form.get('genero')
        descricao = request.form.get('descricao')
        
        # Inicialize o cursor dentro do bloco POST
        with db.cursor() as cursor:
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

    # Lógica para tratamento de GET (Busca e Listagem de Livros)
    search = request.args.get('search')  # Obtém o termo de busca

    # Inicialize o cursor fora do bloco POST para o bloco GET
    with db.cursor() as cursor:
        if search:
            sql = """SELECT id_livro, titulo, isbn, autor, genero, descricao 
                     FROM livros 
                     WHERE disponivel = 1 AND (titulo LIKE %s OR autor LIKE %s OR isbn LIKE %s)"""
            search_term = f"%{search}%"
            cursor.execute(sql, (search_term, search_term, search_term))
        else:
            sql = "SELECT id_livro, titulo, isbn, autor, genero, descricao FROM livros WHERE disponivel = 1"
            cursor.execute(sql)
        
        results = cursor.fetchall()

    # Converta os resultados para uma lista de dicionários
    livros = []
    for row in results:
        livros.append({
            'id': row[0],
            'titulo': row[1],
            'isbn': row[2],
            'autor': row[3],
            'genero': row[4],
            'descricao': row[5]
        })

    return render_template("livros.html", livros=livros, show_navbar=True)

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

    # Lógica para tratamento de POST (Cadastro e Atualização de Empréstimos)
    if request.method == 'POST':
        nome_usuario = request.form.get('nome_usuario')
        id_livro = request.form.get('id_livro')
        data_emprestimo = request.form.get('data_emprestimo')
        data_devolucao = request.form.get('data_devolucao')

        if nome_usuario and id_livro and data_emprestimo and data_devolucao:
            with db.cursor() as cursor:
                # Adiciona um novo empréstimo
                sql = """INSERT INTO emprestimos (nome_usuario, id_livro, data_emprestimo, data_devolucao)
                         VALUES (%s, %s, %s, %s)"""
                cursor.execute(sql, (nome_usuario, id_livro, data_emprestimo, data_devolucao))
                db.commit()

                # Atualiza a disponibilidade do livro
                cursor.execute("UPDATE livros SET disponivel = 0 WHERE id_livro = %s", (id_livro,))
                db.commit()

                # Verifica se o livro está atrasado e move para a tabela de atrasos se necessário
                data_atual = datetime.date.today()
                data_devolucao_date = datetime.datetime.strptime(data_devolucao, "%Y-%m-%d").date()

                if data_atual > data_devolucao_date:
                    sql_atrasos = """INSERT INTO atrasos (id_emprestimo, nome_usuario, nome_livro, 
                                                         data_emprestimo, data_devolucao)
                                     VALUES ((SELECT LAST_INSERT_ID()), %s, (SELECT titulo FROM livros WHERE id_livro = %s), %s, %s)"""
                    cursor.execute(sql_atrasos, (nome_usuario, id_livro, data_emprestimo, data_devolucao))
                    db.commit()

        else:
            return "Todos os campos são obrigatórios!"

    # Lógica para tratamento de GET (Busca e Listagem de Empréstimos)
    search = request.args.get('search')  # Obtém o termo de busca

    with db.cursor() as cursor:
        if search:
            sql = """SELECT emprestimos.id_emprestimo, emprestimos.nome_usuario, livros.titulo, 
                        emprestimos.data_emprestimo, emprestimos.data_devolucao
                     FROM emprestimos
                     JOIN livros ON emprestimos.id_livro = livros.id_livro
                     WHERE (emprestimos.nome_usuario LIKE %s OR livros.titulo LIKE %s)"""
            search_term = f"%{search}%"
            cursor.execute(sql, (search_term, search_term))
        else:
            sql = """SELECT emprestimos.id_emprestimo, emprestimos.nome_usuario, livros.titulo, 
                        emprestimos.data_emprestimo, emprestimos.data_devolucao
                     FROM emprestimos
                     JOIN livros ON emprestimos.id_livro = livros.id_livro"""
            cursor.execute(sql)
        
        emprestimos_result = cursor.fetchall()

        cursor.execute("SELECT * FROM livros WHERE disponivel = 1")
        livros_disponiveis = cursor.fetchall()

    # Converte os resultados para uma lista de dicionários
    emprestimos = []
    for row in emprestimos_result:
        emprestimos.append({
            'id_emprestimo': row[0],
            'nome_usuario': row[1],
            'titulo': row[2],
            'data_emprestimo': row[3].strftime('%Y-%m-%d'),  # Converte datetime para string
            'data_devolucao': row[4].strftime('%Y-%m-%d')   # Converte datetime para string
        })

    livros = []
    for row in livros_disponiveis:
        livros.append({
            'id': row[0],
            'titulo': row[1],
            'isbn': row[2],
            'autor': row[3],
            'genero': row[4],
            'descricao': row[5],
            'disponivel': row[6]
        })

    return render_template("emprestimos.html", emprestimos=emprestimos, livros=livros, show_navbar=True)




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

@app.route("/atrasos")
def atrasos():
    if 'id' not in session:
        return redirect("/")

    cursor = db.cursor()
    sql = """SELECT atrasos.id, atrasos.id_emprestimo, atrasos.nome_usuario, atrasos.nome_livro, 
                    atrasos.data_emprestimo, atrasos.data_devolucao
             FROM atrasos
             JOIN emprestimos ON atrasos.id_emprestimo = emprestimos.id_emprestimo"""
    cursor.execute(sql)
    atrasos = cursor.fetchall()
    
    return render_template("atrasos.html", atrasos=atrasos)

@app.route("/confirmar_devolucao_atraso", methods=['GET'])
def confirmar_devolucao_atraso():
    if 'id' not in session:
        return redirect("/")

    id_emprestimo = request.args.get('id_emprestimo')
    
    cursor = db.cursor()
    
    # Remove o livro da tabela de atrasos
    cursor.execute("DELETE FROM atrasos WHERE id_emprestimo = %s", (id_emprestimo,))
    db.commit()
    
    # Adiciona o livro de volta à tabela de livros
    cursor.execute("SELECT nome_livro FROM emprestimos WHERE id_emprestimo = %s", (id_emprestimo,))
    livro = cursor.fetchone()

    if livro:
        cursor.execute("INSERT INTO livros (titulo, disponivel) VALUES (%s, 1)", (livro[0],))
        db.commit()
    
    # Remove o empréstimo da tabela de emprestimos
    cursor.execute("DELETE FROM emprestimos WHERE id_emprestimo = %s", (id_emprestimo,))
    db.commit()
    
    return redirect("/atrasos", show_navbar = True)


if __name__ == "__main__":
    app.run(debug=True)