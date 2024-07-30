from flask import Flask, render_template, request, redirect, session, jsonify
import datetime
import pymysql

# importacoes

app = Flask(__name__)

app.secret_key = 'eqwivcerldasdkjkgtirrewruywu'
db = pymysql.connect(host="localhost", user="root", password="", database="projetoflask")
# conexao banco

# funcao
@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha').strip()  # o strip remove espaços em branco

        cursor = db.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        usuario = cursor.fetchone()

        if usuario:
            senha_armazenada = usuario[3].strip()  # aqui o 3 ajusta o índice conforme a posição da senha na sua consulta

            if senha_armazenada == senha:
                session['id'] = usuario[0]  # Armazena o ID do usuário na sessão
                return jsonify(success=True, redirect_url="/home")
            else:
                return jsonify(success=False, message="senha_incorreta")
        else:
            return jsonify(success=False, message="email_incorreto")

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
        senha = request.form.get('senha').strip()  # Remove espaços em branco

        if email != confirm_email:
            return jsonify({"success": False, "message": "Os emails não correspondem! Verifique e tente novamente."})

        if not senha or len(senha) < 5:
            return jsonify({"success": False, "message": "A senha deve ter pelo menos 5 caracteres!"})

        cursor = db.cursor()

        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE email = %s", (email,))
        if cursor.fetchone()[0] > 0:
            return jsonify({"success": False, "message": "Este e-mail já está registrado. Escolha outro e-mail."})

        sql = "INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)"
        cursor.execute(sql, (nome, email, senha))
        db.commit()
        return jsonify({"success": True, "redirect_url": "/"})

    return render_template("cadastro.html")

@app.route("/home")
def home():
    if 'id' not in session:
        return redirect("/")
    return render_template("home.html", show_navbar=True, show_footer=True)

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
            # Atualização de livro
            sql = "UPDATE livros SET titulo = %s, isbn = %s, autor = %s, genero = %s, descricao = %s WHERE id_livro = %s"
            cursor.execute(sql, (titulo, isbn, autor, genero, descricao, id_livro))
        else:
            # Verificar se o ISBN já existe
            cursor.execute('SELECT COUNT(*) FROM livros WHERE isbn = %s', (isbn,))
            if cursor.fetchone()[0] == 0:
                # Inserção de livro
                sql = "INSERT INTO livros (titulo, isbn, autor, genero, descricao, disponivel) VALUES (%s, %s, %s, %s, %s, 1)"
                cursor.execute(sql, (titulo, isbn, autor, genero, descricao))
            else:
                return redirect("/livros")  # Evita duplicação

        db.commit()

    search = request.args.get('search')

    cursor = db.cursor()
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

# faz uma lista de acordo com os indices
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

    return render_template("livros.html", livros=livros, show_navbar=True, show_footer=True)


@app.route("/deletar_livro", methods=['GET'])
def deletar_livro():
    if 'id' not in session:
        return redirect("/")

    id_livro = request.args.get('id_livro')
    cursor = db.cursor()
    
    # Remover ou atualizar os empréstimos associados ao livro
    cursor.execute("DELETE FROM emprestimos WHERE id_livro = %s", (id_livro,))
    db.commit()
    
    # Remover o livro
    sql = "DELETE FROM livros WHERE id_livro = %s"
    cursor.execute(sql, (id_livro,))
    db.commit()
    
    return redirect("/livros")

@app.route("/emprestimos", methods=['GET', 'POST'])
def emprestimos():
    if 'id' not in session:
        return redirect("/")

    if request.method == 'POST':
        id_emprestimo = request.form.get('id_emprestimo')
        nome_usuario = request.form.get('nome_usuario')
        id_livro = request.form.get('id_livro')
        data_emprestimo = request.form.get('data_emprestimo')
        data_devolucao = request.form.get('data_devolucao')

        cursor = db.cursor()
        if id_emprestimo:
            sql = """UPDATE emprestimos 
                     SET nome_usuario = %s, id_livro = %s, data_emprestimo = %s, data_devolucao = %s 
                     WHERE id_emprestimo = %s"""
            cursor.execute(sql, (nome_usuario, id_livro, data_emprestimo, data_devolucao, id_emprestimo))
        else:
            sql = """INSERT INTO emprestimos (nome_usuario, id_livro, data_emprestimo, data_devolucao)
                     VALUES (%s, %s, %s, %s)"""
            cursor.execute(sql, (nome_usuario, id_livro, data_emprestimo, data_devolucao))
            
            # Atualiza a disponibilidade do livro
            cursor.execute("UPDATE livros SET disponivel = 0 WHERE id_livro = %s", (id_livro,))

        db.commit()

    search = request.args.get('search')

    cursor = db.cursor()
    if search:
        sql = """SELECT e.id_emprestimo, e.nome_usuario, l.titulo AS nome_livro, e.data_emprestimo, e.data_devolucao
                 FROM emprestimos e
                 JOIN livros l ON e.id_livro = l.id_livro
                 WHERE l.titulo LIKE %s OR e.nome_usuario LIKE %s"""
        search_term = f"%{search}%"
        cursor.execute(sql, (search_term, search_term))
    else:
        sql = """SELECT e.id_emprestimo, e.nome_usuario, l.titulo AS nome_livro, e.data_emprestimo, e.data_devolucao
                 FROM emprestimos e
                 JOIN livros l ON e.id_livro = l.id_livro"""
        cursor.execute(sql)

    results = cursor.fetchall()

    emprestimos = []
    for row in results:
        emprestimos.append({
            'id_emprestimo': row[0],
            'nome_usuario': row[1],
            'id_livro': row[2],  # Se não precisar do id_livro, pode remover
            'nome_livro': row[2],  # Nome do livro
            'data_emprestimo': row[3],
            'data_devolucao': row[4]
        })

    cursor.execute("SELECT id_livro, titulo FROM livros WHERE disponivel = 1")
    livros_results = cursor.fetchall()

    livros = []
    for row in livros_results:
        livros.append({
            'id': row[0],
            'titulo': row[1]
        })

    return render_template("emprestimos.html", emprestimos=emprestimos, livros=livros, show_navbar=True, show_footer=True)

@app.route("/editar_emprestimo", methods=['POST'])
def editar_emprestimo():
    if 'id' not in session:
        return redirect("/")
    
    id_emprestimo = request.form.get('id_emprestimo')
    nome_usuario = request.form.get('nome_usuario')
    data_emprestimo = request.form.get('data_emprestimo')
    data_devolucao = request.form.get('data_devolucao')
    
    cursor = db.cursor()
    
    # Atualizar dados do empréstimo
    sql = """UPDATE emprestimos
             SET nome_usuario = %s, data_emprestimo = %s, data_devolucao = %s
             WHERE id_emprestimo = %s"""
    cursor.execute(sql, (nome_usuario, data_emprestimo, data_devolucao, id_emprestimo))
    
    # Atualizar disponibilidade do livro (se necessário)
    cursor.execute("SELECT id_livro FROM emprestimos WHERE id_emprestimo = %s", (id_emprestimo,))
    id_livro_atual = cursor.fetchone()[0]
    novo_id_livro = request.form.get('id_livro')

    if novo_id_livro and novo_id_livro != str(id_livro_atual):
        cursor.execute("UPDATE livros SET disponivel = 1 WHERE id_livro = %s", (id_livro_atual,))
        cursor.execute("UPDATE livros SET disponivel = 0 WHERE id_livro = %s", (novo_id_livro,))
        cursor.execute("UPDATE emprestimos SET id_livro = %s WHERE id_emprestimo = %s", (novo_id_livro, id_emprestimo))
    
    db.commit()
    
    return redirect("/emprestimos")



@app.route("/confirmar_devolucao", methods=['GET'])
def confirmar_devolucao():
    if 'id' not in session:
        return redirect("/")

    id_emprestimo = request.args.get('id_emprestimo')
    
    cursor = db.cursor()
    
    # Salva o id_livro antes de remover o empréstimo
    cursor.execute("SELECT id_livro FROM emprestimos WHERE id_emprestimo = %s", (id_emprestimo,))
    result = cursor.fetchone()
    if result:
        id_livro = result[0]
    else:
        return "Empréstimo não encontrado!"
    
    # Remove o registro da tabela de atrasos se existir
    cursor.execute("DELETE FROM atrasos WHERE id_emprestimo = %s", (id_emprestimo,))
    db.commit()
    
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
    
    # SQL para encontrar livros que passaram da data de devolução e não foram devolvidos
    sql = """SELECT e.id_emprestimo, e.nome_usuario, l.titulo AS nome_livro, e.data_emprestimo, e.data_devolucao
             FROM emprestimos e
             JOIN livros l ON e.id_livro = l.id_livro
             WHERE e.data_devolucao < CURDATE() AND e.id_emprestimo NOT IN (
                 SELECT id_emprestimo FROM devolucoes_confirmadas
             )"""
             
    cursor.execute(sql)
    results = cursor.fetchall()

    atrasos = []
    for row in results:
        atrasos.append({
            'id_emprestimo': row[0],
            'nome_usuario': row[1],
            'nome_livro': row[2],
            'data_emprestimo': row[3],
            'data_devolucao': row[4]
        })

    return render_template("atrasos.html", atrasos=atrasos, show_navbar=True, show_footer=True)

@app.route("/confirmar_devolucao_atraso")
def confirmar_devolucao_atraso():
    if 'id' not in session:
        return redirect("/")

    id_emprestimo = request.args.get('id_emprestimo')
    
    cursor = db.cursor()
    
    # Atualiza a tabela de devoluções confirmadas
    sql = """INSERT INTO devolucoes_confirmadas (id_emprestimo) VALUES (%s)"""
    cursor.execute(sql, (id_emprestimo,))
    
    db.commit()
    
    # Atualiza a disponibilidade do livro
    cursor.execute("UPDATE livros SET disponivel = 1 WHERE id_livro = (SELECT id_livro FROM emprestimos WHERE id_emprestimo = %s)", (id_emprestimo,))
    
    db.commit()
    
    return redirect("/atrasos")

@app.route("/save_initial_setup", methods=['POST'])
def save_initial_setup():
    data = request.json
    library_name = data.get('libraryName')

    session['library_name'] = library_name
    
    return jsonify({'status': 'success'})


if __name__ == "__main__":
    app.run(debug=True)
