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
        email = request.form.get('email').strip()  # remove espaços em branco ao redor do email
        senha = request.form.get('senha').strip()  # remove espaços em branco ao redor da senha

        cursor = db.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        usuario = cursor.fetchone()

        if usuario:
            senha_armazenada = usuario[4].strip()  # ajusta o índice conforme a posição da senha na sua consulta

            if senha_armazenada == senha:
                session['id'] = usuario[0]  # srmazena o ID do usuário na sessão
                return jsonify(success=True, redirect_url="/home")
            else:
                return jsonify(success=False, message="Senha incorreta. Verifique e tente novamente.")
        else:
            return jsonify(success=False, message="Email não registrado. Verifique e tente novamente.")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop('id', None)  # remove o ID do usuário da sessão
    return redirect("/")

@app.route("/cadastro", methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        confirm_email = request.form.get('confirm_email')
        senha = request.form.get('senha').strip()  # remove espaços em branco
        nome_biblioteca = request.form.get('nome_biblioteca')

        if email != confirm_email:
            return jsonify({"success": False, "message": "Os emails não correspondem! Verifique e tente novamente."})

        if not senha or len(senha) < 5:
            return jsonify({"success": False, "message": "A senha deve ter pelo menos 5 caracteres!"})

        cursor = db.cursor()

        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE email = %s", (email,))
        if cursor.fetchone()[0] > 0:
            return jsonify({"success": False, "message": "Este e-mail já está registrado. Escolha outro e-mail."})

        sql = "INSERT INTO usuarios (nome, email, senha, nome_biblioteca) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (nome, email, senha, nome_biblioteca))
        db.commit()
        return jsonify({"success": True, "redirect_url": "/"})

    return render_template("cadastro.html")

@app.route("/home")
def home():
    if 'id' not in session:
        return redirect("/")

    id_usuario = session['id']
    
    cursor = db.cursor()

    # buscar nome da biblioteca
    cursor.execute("SELECT nome_biblioteca FROM usuarios WHERE id_usuario = %s", (id_usuario,))
    result = cursor.fetchone()
    library_name = result[0] if result else "Nome da Biblioteca Desconhecido"
    
    # contar livros cadastrados
    cursor.execute("SELECT COUNT(*) FROM livros WHERE id_usuario = %s", (id_usuario,))
    num_livros = cursor.fetchone()[0]
    
    # contar livros emprestados
    cursor.execute("SELECT COUNT(*) FROM emprestimos WHERE id_usuario = %s", (id_usuario,))
    num_emprestados = cursor.fetchone()[0]
    
    # contar atrasos
    cursor.execute("""SELECT COUNT(*) FROM emprestimos
                      WHERE data_devolucao < CURDATE() AND id_usuario = %s AND id_emprestimo NOT IN (
                          SELECT id_emprestimo FROM devolucoes_confirmadas
                      )""", (id_usuario,))
    num_atrasos = cursor.fetchone()[0]

    return render_template("home.html", 
                           show_navbar=True, 
                           show_footer=True, 
                           num_livros=num_livros, 
                           num_emprestados=num_emprestados, 
                           num_atrasos=num_atrasos,
                           library_name=library_name)

@app.route("/livros", methods=['GET', 'POST'])
def livros():
    if 'id' not in session:
        return redirect("/")

    id_usuario = session['id']

    if request.method == 'POST':
        id_livro = request.form.get('id_livro')
        titulo = request.form.get('titulo')
        isbn = request.form.get('isbn')
        autor = request.form.get('autor')
        genero = request.form.get('genero')
        descricao = request.form.get('descricao')

        cursor = db.cursor()
        if id_livro:
            # atualização de livro
            sql = "UPDATE livros SET titulo = %s, isbn = %s, autor = %s, genero = %s, descricao = %s WHERE id_livro = %s AND id_usuario = %s"
            cursor.execute(sql, (titulo, isbn, autor, genero, descricao, id_livro, id_usuario))
        else:
            # verificar se o ISBN já existe
            cursor.execute('SELECT COUNT(*) FROM livros WHERE isbn = %s AND id_usuario = %s', (isbn, id_usuario))
            if cursor.fetchone()[0] == 0:
                # nnserção de livro
                sql = "INSERT INTO livros (titulo, isbn, autor, genero, descricao, disponivel, id_usuario) VALUES (%s, %s, %s, %s, %s, 1, %s)"
                cursor.execute(sql, (titulo, isbn, autor, genero, descricao, id_usuario))
            else:
                return redirect("/livros")  # evita duplicação

        db.commit()

    search = request.args.get('search')

    cursor = db.cursor()
    if search:
        sql = """SELECT id_livro, titulo, isbn, autor, genero, descricao 
                 FROM livros 
                 WHERE disponivel = 1 AND id_usuario = %s AND (titulo LIKE %s OR autor LIKE %s OR isbn LIKE %s)"""
        search_term = f"%{search}%"
        cursor.execute(sql, (id_usuario, search_term, search_term, search_term))
    else:
        sql = "SELECT id_livro, titulo, isbn, autor, genero, descricao FROM livros WHERE disponivel = 1 AND id_usuario = %s"
        cursor.execute(sql, (id_usuario,))

    results = cursor.fetchall()

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
    
    mensagem = None

    if search and not livros:
        mensagem = "Livro não encontrado."

    return render_template("livros.html", livros=livros, show_navbar=True, show_footer=True, mensagem=mensagem)

@app.route("/deletar_livro", methods=['GET'])
def deletar_livro():
    if 'id' not in session:
        return redirect("/")

    id_livro = request.args.get('id_livro')
    cursor = db.cursor()
    
    # remover ou atualizar os empréstimos associados ao livro
    cursor.execute("DELETE FROM emprestimos WHERE id_livro = %s", (id_livro,))
    db.commit()
    
    # remover o livro
    sql = "DELETE FROM livros WHERE id_livro = %s"
    cursor.execute(sql, (id_livro,))
    db.commit()
    
    return redirect("/livros")

@app.route("/emprestimos", methods=['GET', 'POST'])
def emprestimos():
    if 'id' not in session:
        return redirect("/")

    id_usuario = session['id']

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
                     WHERE id_emprestimo = %s AND id_usuario = %s"""
            cursor.execute(sql, (nome_usuario, id_livro, data_emprestimo, data_devolucao, id_emprestimo, id_usuario))
        else:
            sql = """INSERT INTO emprestimos (nome_usuario, id_livro, data_emprestimo, data_devolucao, id_usuario)
                     VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(sql, (nome_usuario, id_livro, data_emprestimo, data_devolucao, id_usuario))
            
            # atualiza a disponibilidade do livro
            cursor.execute("UPDATE livros SET disponivel = 0 WHERE id_livro = %s AND id_usuario = %s", (id_livro, id_usuario))

        db.commit()

    search = request.args.get('search')

    cursor = db.cursor()
    if search:
        sql = """SELECT e.id_emprestimo, e.nome_usuario, l.titulo AS nome_livro, e.data_emprestimo, e.data_devolucao
                 FROM emprestimos e
                 JOIN livros l ON e.id_livro = l.id_livro
                 WHERE e.id_usuario = %s AND (l.titulo LIKE %s OR e.nome_usuario LIKE %s)"""
        search_term = f"%{search}%"
        cursor.execute(sql, (id_usuario, search_term, search_term))
    else:
        sql = """SELECT e.id_emprestimo, e.nome_usuario, l.titulo AS nome_livro, e.data_emprestimo, e.data_devolucao
                 FROM emprestimos e
                 JOIN livros l ON e.id_livro = l.id_livro
                 WHERE e.id_usuario = %s"""
        cursor.execute(sql, (id_usuario,))

    results = cursor.fetchall()

    emprestimos = []
    for row in results:
        emprestimos.append({
            'id_emprestimo': row[0],
            'nome_usuario': row[1],
            'id_livro': row[2],  # se não precisar do id_livro, pode remover
            'nome_livro': row[2],  # nome do livro
            'data_emprestimo': row[3],
            'data_devolucao': row[4]
        })

    cursor.execute("SELECT id_livro, titulo FROM livros WHERE disponivel = 1 AND id_usuario = %s", (id_usuario,))
    livros_results = cursor.fetchall()

    livros = []
    for row in livros_results:
        livros.append({
            'id': row[0],
            'titulo': row[1]
        })

    mensagem = None

    if search and not emprestimos:
        mensagem = "Livro emprestado não encontrado."

    return render_template("emprestimos.html", emprestimos=emprestimos, livros=livros, show_navbar=True, show_footer=True, mensagem=mensagem)

@app.route("/editar_emprestimo", methods=['POST'])
def editar_emprestimo():
    if 'id' not in session:
        return redirect("/")
    
    id_emprestimo = request.form.get('id_emprestimo')
    nome_usuario = request.form.get('nome_usuario')
    data_emprestimo = request.form.get('data_emprestimo')
    data_devolucao = request.form.get('data_devolucao')
    
    cursor = db.cursor()
    
    # atualizar dados do empréstimo
    sql = """UPDATE emprestimos
             SET nome_usuario = %s, data_emprestimo = %s, data_devolucao = %s
             WHERE id_emprestimo = %s"""
    cursor.execute(sql, (nome_usuario, data_emprestimo, data_devolucao, id_emprestimo))
    
    # atualizar disponibilidade do livro (se necessário)
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
    
    # salva o id_livro antes de remover o empréstimo
    cursor.execute("SELECT id_livro FROM emprestimos WHERE id_emprestimo = %s", (id_emprestimo,))
    result = cursor.fetchone()
    if result:
        id_livro = result[0]
    else:
        return "Empréstimo não encontrado!"
    
    # remove o registro da tabela de atrasos se existir
    cursor.execute("DELETE FROM atrasos WHERE id_emprestimo = %s", (id_emprestimo,))
    db.commit()
    
    # remove o empréstimo
    cursor.execute("DELETE FROM emprestimos WHERE id_emprestimo = %s", (id_emprestimo,))
    db.commit()
    
    # atualiza a disponibilidade do livro
    cursor.execute("UPDATE livros SET disponivel = 1 WHERE id_livro = %s", (id_livro,))
    db.commit()
    
    return redirect("/emprestimos")

@app.route("/atrasos")
def atrasos():
    if 'id' not in session:
        return redirect("/")

    id_usuario = session['id']
    
    cursor = db.cursor()
    
    # SQL para encontrar livros que passaram da data de devolução e não foram devolvidos
    sql = """SELECT e.id_emprestimo, e.nome_usuario, l.titulo AS nome_livro, e.data_emprestimo, e.data_devolucao
             FROM emprestimos e
             JOIN livros l ON e.id_livro = l.id_livro
             WHERE e.data_devolucao < CURDATE() AND e.id_usuario = %s AND e.id_emprestimo NOT IN (
                 SELECT id_emprestimo FROM devolucoes_confirmadas
             )"""
             
    cursor.execute(sql, (id_usuario,))
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
    
    # atualiza a tabela de devoluções confirmadas
    sql = """INSERT INTO devolucoes_confirmadas (id_emprestimo) VALUES (%s)"""
    cursor.execute(sql, (id_emprestimo,))
    
    db.commit()
    
    # atualiza a disponibilidade do livro
    cursor.execute("UPDATE livros SET disponivel = 1 WHERE id_livro = (SELECT id_livro FROM emprestimos WHERE id_emprestimo = %s)", (id_emprestimo,))
    
    db.commit()
    
    return redirect("/atrasos")

@app.route("/save_initial_setup", methods=['POST'])
def save_initial_setup():
    data = request.json
    library_name = data.get('libraryName')

    session['library_name'] = library_name
    
    return jsonify({'status': 'success'})

@app.route("/perfil")
def perfil():
    if 'id' not in session:
        return redirect("/")

    id_usuario = session['id']

    cursor = db.cursor()
    cursor.execute("SELECT nome, email, nome_biblioteca FROM usuarios WHERE id_usuario = %s", (id_usuario,))
    user_info = cursor.fetchone()

    if user_info:
        nome, email, nome_biblioteca = user_info
        return render_template("perfil.html", 
                               nome=nome, 
                               email=email, 
                               nome_biblioteca=nome_biblioteca, 
                               show_navbar=True, 
                               show_footer=True)
    else:
        return redirect("/")

@app.route("/atualizar_perfil", methods=['POST'])
def atualizar_perfil():
    if 'id' not in session:
        return redirect("/")

    id_usuario = session['id']
    novo_nome = request.form.get('novo_nome').strip()
    novo_email = request.form.get('novo_email').strip()
    nova_senha = request.form.get('nova_senha').strip()
    novo_nome_biblioteca = request.form.get('novo_nome_biblioteca').strip()

    cursor = db.cursor()

    # obtemos a senha atual do usuário
    cursor.execute("SELECT senha FROM usuarios WHERE id_usuario = %s", (id_usuario,))
    senha_atual = cursor.fetchone()[0]

    if nova_senha:
        senha_para_atualizar = nova_senha
    else:
        senha_para_atualizar = senha_atual

    # atualiza as informações do perfil
    sql = """UPDATE usuarios
             SET nome = %s, email = %s, senha = %s, nome_biblioteca = %s
             WHERE id_usuario = %s"""
    cursor.execute(sql, (novo_nome, novo_email, senha_para_atualizar, novo_nome_biblioteca, id_usuario))

    db.commit()
    
    return redirect("/perfil")

@app.route("/apagar_conta", methods=['POST'])
def apagar_conta():
    if 'id' not in session:
        return redirect("/")

    id_usuario = session['id']

    cursor = db.cursor()

    # remove empréstimos associados
    cursor.execute("DELETE FROM emprestimos WHERE id_usuario = %s", (id_usuario,))
    
    # remove reservas associadas (se houver)
    cursor.execute("DELETE FROM atrasos WHERE id_usuario = %s", (id_usuario,))

    # remove o usuário
    cursor.execute("DELETE FROM usuarios WHERE id_usuario = %s", (id_usuario,))
    db.commit()

    # remove a sessão do usuário
    session.pop('id', None)
    
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
