function openCadastroModal() {
    document.getElementById('cadastroModal').style.display = "block";
}

function closeCadastroModal() {
    document.getElementById('cadastroModal').style.display = "none";
}

function openEditModal(id, titulo, isbn, autor, genero, descricao) {
    document.getElementById('edit-id_livro').value = id;
    document.getElementById('edit-titulo').value = titulo;
    document.getElementById('edit-isbn').value = isbn;
    document.getElementById('edit-autor').value = autor;
    document.getElementById('edit-genero').value = genero;
    document.getElementById('edit-descricao').value = descricao;
    
    document.getElementById('editModal').style.display = "block";
    document.getElementById('deleteButton').style.display = "inline";
}

function closeEditModal() {
    document.getElementById('editModal').style.display = "none";
    document.getElementById('deleteButton').style.display = "none";
}

function deleteLivro() {
    var id_livro = document.getElementById('edit-id_livro').value;
    if (confirm("Tem certeza de que deseja deletar este livro?")) {
        window.location.href = "/deletar_livro?id_livro=" + id_livro;
    }
}

window.onclick = function(event) {
    if (event.target == document.getElementById('cadastroModal')) {
        closeCadastroModal();
    }
    if (event.target == document.getElementById('editModal')) {
        closeEditModal();
    }
}