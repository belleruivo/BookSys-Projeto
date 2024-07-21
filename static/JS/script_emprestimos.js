// Funções para abrir e fechar o modal de cadastro
function openCadastroModal() {
    document.getElementById("cadastroModal").style.display = "block";
}

function closeCadastroModal() {
    document.getElementById("cadastroModal").style.display = "none";
}

// Funções para abrir e fechar o modal de edição
function openEditarModal(id_emprestimo, nome_usuario, id_livro, data_emprestimo, data_devolucao) {
    document.getElementById("editarModal").style.display = "block";
    document.getElementById("edit_id_emprestimo").value = id_emprestimo;
    document.getElementById("edit_nome_usuario").value = nome_usuario;
    document.getElementById("edit_id_livro").value = id_livro;
    document.getElementById("edit_data_emprestimo").value = data_emprestimo;
    document.getElementById("edit_data_devolucao").value = data_devolucao;
}

function closeEditarModal() {
    document.getElementById("editarModal").style.display = "none";
}

// Fechar modais ao clicar fora do conteúdo
window.onclick = function(event) {
    if (event.target == document.getElementById("cadastroModal")) {
        closeCadastroModal();
    }
    if (event.target == document.getElementById("editarModal")) {
        closeEditarModal();
    }
}
