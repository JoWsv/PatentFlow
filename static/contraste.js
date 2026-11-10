
document.addEventListener('DOMContentLoaded', function () {
    const botao = document.getElementById('botao-contraste');

    if (!botao) return;

    function atualizarContraste(ativo) {
        document.body.classList.toggle('alto-contraste', ativo);

        botao.setAttribute('aria-pressed', String(ativo));
        botao.setAttribute(
            'aria-label',
            ativo ? 'Desativar alto contraste' : 'Ativar alto contraste'
        );

        botao.textContent = ativo
            ? 'Contraste normal'
            : 'Alto contraste';
    }

    atualizarContraste(
        localStorage.getItem('patentflow-contraste') === 'ativo'
    );

    botao.addEventListener('click', function () {
        const ativo = !document.body.classList.contains('alto-contraste');

        atualizarContraste(ativo);

        localStorage.setItem(
            'patentflow-contraste',
            ativo ? 'ativo' : 'normal'
        );
    });
});
