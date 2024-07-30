function openCadastroModal() {
    document.getElementById('cadastroModal').style.display = "block";
}

function closeCadastroModal() {
    document.getElementById('cadastroModal').style.display = "none";
}

function openEditModal(id, nome_usuario, titulo_livro, data_emprestimo, data_devolucao) {
    document.getElementById('edit_id_emprestimo').value = id;
    document.getElementById('edit_nome_usuario').value = nome_usuario;
    document.getElementById('edit_titulo_livro').value = titulo_livro;  
    document.getElementById('edit_data_emprestimo').value = data_emprestimo;
    document.getElementById('edit_data_devolucao').value = data_devolucao;

    document.getElementById('editModal').style.display = "block";
}

function closeEditModal() {
    document.getElementById('editModal').style.display = "none";
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
