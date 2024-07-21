from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)

app.secret_key = 'eqwivcerldasdkjkgtirrewruywu'
# db = pymysql.connect(host="localhost", user="root", password="", database="projetoflask")

usuarios = [{'id': 1, 'email': 'usuario@example.com', 'senha': 'senha123', 'nome': 'Usuário Exemplo'}]
livros_mockados = [
    {'id': 1, 'titulo': 'Livro 1', 'isbn': '1234567890', 'autor': 'Autor 1', 'genero': 'Ficção', 'descricao': 'Descrição 1', 'disponivel': True},
    {'id': 2, 'titulo': 'Livro 2', 'isbn': '0987654321', 'autor': 'Autor 2', 'genero': 'Drama', 'descricao': 'Descrição 2', 'disponivel': True},
    {'id': 3, 'titulo': 'Livro 3', 'isbn': '1234567890', 'autor': 'Autor 1', 'genero': 'Ficção', 'descricao': 'Descrição 1', 'disponivel': True},
    {'id': 4, 'titulo': 'Livro 4', 'isbn': '0987654321', 'autor': 'Autor 2', 'genero': 'Drama', 'descricao': 'Descrição 2', 'disponivel': True},
    {'id': 5, 'titulo': 'Livro 5', 'isbn': '1234567890', 'autor': 'Autor 1', 'genero': 'Ficção', 'descricao': 'Descrição 1', 'disponivel': True},
    {'id': 6, 'titulo': 'Livro 6', 'isbn': '0987654321', 'autor': 'Autor 2', 'genero': 'Drama', 'descricao': 'Descrição 2', 'disponivel': True},
    {'id': 7, 'titulo': 'Livro 7', 'isbn': '0987654321', 'autor': 'Autor 2', 'genero': 'Drama', 'descricao': 'Descrição 2', 'disponivel': True},
    {'id': 8, 'titulo': 'Livro 8', 'isbn': '1234567890', 'autor': 'Autor 1', 'genero': 'Ficção', 'descricao': 'Descrição 1', 'disponivel': True},
]

emprestimos_mockados = [
    {'id_emprestimo': 1, 'nome_usuario': 'João Silva', 'id_livro': 1, 'data_emprestimo': '2024-01-10', 'data_devolucao': '2024-02-10'},
    {'id_emprestimo': 2, 'nome_usuario': 'Maria Oliveira', 'id_livro': 2, 'data_emprestimo': '2024-02-01', 'data_devolucao': '2024-03-01'},
    {'id_emprestimo': 3, 'nome_usuario': 'Carlos Pereira', 'id_livro': 3, 'data_emprestimo': '2024-03-15', 'data_devolucao': '2024-04-15'},
    {'id_emprestimo': 4, 'nome_usuario': 'Ana Costa', 'id_livro': 4, 'data_emprestimo': '2024-04-01', 'data_devolucao': '2024-05-01'},
    {'id_emprestimo': 5, 'nome_usuario': 'Fernanda Souza', 'id_livro': 5, 'data_emprestimo': '2024-05-10', 'data_devolucao': '2024-06-10'},
    {'id_emprestimo': 6, 'nome_usuario': 'Pedro Santos', 'id_livro': 6, 'data_emprestimo': '2024-06-20', 'data_devolucao': '2024-07-20'},
    {'id_emprestimo': 7, 'nome_usuario': 'Fernanda Souza', 'id_livro': 5, 'data_emprestimo': '2024-05-10', 'data_devolucao': '2024-06-10'},
    {'id_emprestimo': 8, 'nome_usuario': 'Pedro Santos', 'id_livro': 6, 'data_emprestimo': '2024-06-20', 'data_devolucao': '2024-07-20'},
]

@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        usuario = next((u for u in usuarios if u['email'] == email and u['senha'] == senha), None)
        if usuario:
            session['id'] = usuario['id']
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
            usuarios.append({'id': len(usuarios) + 1, 'email': email, 'senha': senha, 'nome': nome})
            return redirect("/")
        else:
            return "Os emails não correspondem!"
    
    return render_template("cadastro.html")

@app.route("/home")
def home():
    if 'id' not in session:
        return redirect("/")
    return render_template("home.html", show_navbar=True)

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

        if id_livro:
            id_livro = int(id_livro)
            for livro in livros_mockados:
                if livro['id'] == id_livro:
                    livro.update({
                        'titulo': titulo,
                        'isbn': isbn,
                        'autor': autor,
                        'genero': genero,
                        'descricao': descricao
                    })
                    break
        else:
            if not any(livro['isbn'] == isbn for livro in livros_mockados):
                novo_livro = {
                    'id': len(livros_mockados) + 1,
                    'titulo': titulo,
                    'isbn': isbn,
                    'autor': autor,
                    'genero': genero,
                    'descricao': descricao,
                    'disponivel': True
                }
                livros_mockados.append(novo_livro)
            else:
                return redirect("/livros")

    search_query = request.args.get('search', '').lower()
    
    results = [
        livro for livro in livros_mockados if livro['disponivel'] and (
            search_query in livro['titulo'].lower() or
            search_query in livro['autor'].lower() or
            search_query in livro['isbn']
        )
    ]

    return render_template("livros.html", livros=results, show_navbar=True)

@app.route("/deletar_livro", methods=['GET'])
def deletar_livro():
    if 'id' not in session:
        return redirect("/")
    
    id_livro = request.args.get('id_livro')
    global livros_mockados
    livros_mockados = [livro for livro in livros_mockados if livro['id'] != int(id_livro)]
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
            id_livro = int(id_livro)
            emprestimos_mockados.append({
                'id_emprestimo': len(emprestimos_mockados) + 1,
                'nome_usuario': nome_usuario,
                'id_livro': id_livro,
                'data_emprestimo': data_emprestimo,
                'data_devolucao': data_devolucao
            })
            
            for livro in livros_mockados:
                if livro['id'] == id_livro:
                    livro['disponivel'] = False
                    break
        else:
            return "Todos os campos são obrigatórios!"

    emprestimos_exibidos = [
        {
            'id_emprestimo': emp['id_emprestimo'],
            'nome_usuario': emp['nome_usuario'],
            'id_livro': emp['id_livro'],
            'titulo': next(livro['titulo'] for livro in livros_mockados if livro['id'] == emp['id_livro']),
            'data_emprestimo': emp['data_emprestimo'],
            'data_devolucao': emp['data_devolucao']
        }
        for emp in emprestimos_mockados
    ]

    livros_disponiveis = [livro for livro in livros_mockados if livro['disponivel']]

    return render_template("emprestimos.html", emprestimos=emprestimos_exibidos, livros=livros_disponiveis, show_navbar=True)


@app.route("/editar_emprestimo", methods=['POST'])
def editar_emprestimo():
    if 'id' not in session:
        return redirect("/")
    
    id_emprestimo = request.form.get('id_emprestimo')
    nome_usuario = request.form.get('nome_usuario')
    id_livro = request.form.get('id_livro')
    data_emprestimo = request.form.get('data_emprestimo')
    data_devolucao = request.form.get('data_devolucao')
    
    id_emprestimo = int(id_emprestimo)
    
    for emp in emprestimos_mockados:
        if emp['id_emprestimo'] == id_emprestimo:
            emp.update({
                'nome_usuario': nome_usuario,
                'id_livro': int(id_livro),
                'data_emprestimo': data_emprestimo,
                'data_devolucao': data_devolucao
            })
            break
    
    return redirect("/emprestimos")

@app.route("/confirmar_devolucao", methods=['GET'])
def confirmar_devolucao():
    if 'id' not in session:
        return redirect("/")
    
    id_emprestimo = request.args.get('id_emprestimo')
    id_emprestimo = int(id_emprestimo)
    
    global emprestimos_mockados
    emprestimo = next((emp for emp in emprestimos_mockados if emp['id_emprestimo'] == id_emprestimo), None)
    if emprestimo:
        id_livro = emprestimo['id_livro']
        
        emprestimos_mockados = [emp for emp in emprestimos_mockados if emp['id_emprestimo'] != id_emprestimo]
        
        for livro in livros_mockados:
            if livro['id'] == id_livro:
                livro['disponivel'] = True
                break
    
    return redirect("/emprestimos")

@app.route("/atrasos")
def atrasos():
    if 'id' not in session:
        return redirect("/")

    # Simula a consulta de atrasos
    atrasos_exibidos = [
        {
            'id': emp['id_emprestimo'],
            'nome_usuario': emp['nome_usuario'],
            'titulo': next(livro['titulo'] for livro in livros_mockados if livro['id'] == emp['id_livro']),
            'data_emprestimo': emp['data_emprestimo'],
            'data_devolucao': emp['data_devolucao']
        }
        for emp in emprestimos_mockados
        if emp['data_devolucao'] < '2024-07-21'  # Adicione lógica de atraso conforme necessário
    ]
    
    return render_template("atrasos.html", atrasos=atrasos_exibidos, show_navbar=True)

@app.route("/confirmar_devolucao_atraso", methods=['GET'])
def confirmar_devolucao_atraso():
    if 'id' not in session:
        return redirect("/")

    id_emprestimo = request.args.get('id_emprestimo')
    id_emprestimo = int(id_emprestimo)
    
    # Remove o atraso da lista
    global emprestimos_mockados
    emprestimos_mockados = [emp for emp in emprestimos_mockados if emp['id_emprestimo'] != id_emprestimo]
    
    # Atualiza a disponibilidade do livro
    for livro in livros_mockados:
        if livro['id'] == id_emprestimo:
            livro['disponivel'] = True
            break
    
    return redirect("/atrasos")

if __name__ == "__main__":
    app.run(debug=True)
