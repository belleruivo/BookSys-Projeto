function openCadastroModal() {
    document.getElementById('cadastroModal').style.display = "block";
}

function closeCadastroModal() {
    document.getElementById('cadastroModal').style.display = "none";
}

function openEditModal(id, nome_usuario, nome_livro, data_emprestimo, data_devolucao) {
    document.getElementById('edit-id_emprestimo').value = id;
    document.getElementById('edit-nome_usuario').value = nome_usuario;
    document.getElementById('edit-nome_livro').value = nome_livro;
    document.getElementById('edit-data_emprestimo').value = data_emprestimo;
    document.getElementById('edit-data_devolucao').value = data_devolucao;
    
    document.getElementById('editModal').style.display = "block";
    document.getElementById('devolucaoButton').style.display = "inline";
}

function closeEditModal() {
    document.getElementById('editModal').style.display = "none";
    document.getElementById('devolucaoButton').style.display = "none";
}

function confirmarDevolucao(id) {
    if (confirm("Tem certeza de que deseja confirmar a devolução deste empréstimo?")) {
        window.location.href = "/confirmar_devolucao?id_emprestimo=" + id;
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
