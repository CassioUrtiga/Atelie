function paraCapitalize(texto) {
    if (!texto) return '';
    const textoLimpo = texto.trim();
    return textoLimpo.charAt(0).toUpperCase() + textoLimpo.slice(1).toLowerCase();
}


// Lógica de desmarcar checkbox (filtros)
document.addEventListener("DOMContentLoaded", function() {
    const checkTodosPedidos = document.getElementById('checkTodosPedidos');
    const checkTodosClientes = document.getElementById('checkTodosClientes');

    const outrosFiltrosPedidos = document.querySelectorAll('input[name="status_filtro_pedidos"]:not(#checkTodosPedidos)');
    const outrosFiltrosClientes = document.querySelectorAll('input[name="status_filtro_clientes"]:not(#checkTodosClientes)');

    // Cenário 1: Se o usuário clicar em "Todos", desmarca todos os outros
    checkTodosPedidos.addEventListener('change', function() {
        if (this.checked) {
            outrosFiltrosPedidos.forEach(checkbox => {
                checkbox.checked = false;
            });
        }
    });

    checkTodosClientes.addEventListener('change', function() {
        if (this.checked) {
            outrosFiltrosClientes.forEach(checkbox => {
                checkbox.checked = false;
            });
        }
    });

    // Cenário 2: Se o usuário marcar qualquer outro filtro, desmarca o "Todos"
    outrosFiltrosPedidos.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                checkTodosPedidos.checked = false;
            }
        });
    });

    outrosFiltrosClientes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                checkTodosClientes.checked = false;
            }
        });
    });
});

// Adicionar as tags nos campos inputs de serviços/roupas/tecidos
document.querySelectorAll('.tag-wrapper').forEach(wrapper => {
    const tagContainer = wrapper.querySelector('.tag-container');
    const tagInput = wrapper.querySelector('.tag-input');
    const inputEscondido = wrapper.querySelector('.itens-escondidos');
    
    let listaDeItens = [];

    // Carrega as tags predefinidas
    wrapper.querySelectorAll('.btn-remover-predefinido').forEach(botao => {
        const valorPredefinido = botao.getAttribute('data-item').trim();
        
        if (valorPredefinido) {
            listaDeItens.push(valorPredefinido);
        }

        // Adiciona o evento de remover para as tags que já vieram prontas
        botao.addEventListener('click', (evento) => {
            evento.stopPropagation();
            botao.closest('.tag-predefinida').remove();
            listaDeItens = listaDeItens.filter(item => item !== valorPredefinido);
            atualizarInputEscondido();
        });
    });

    // Foca no input quando clicar na caixa cinza deste bloco
    tagContainer.addEventListener('click', () => {
        tagInput.focus();
    });

    // Escuta as teclas digitadas
    tagInput.addEventListener('keyup', function(e) {
        if (e.key === 'Enter' || e.key === ',') {
            e.preventDefault();
            
            // 1. Limpa espaços e vírgulas
            let valorCru = tagInput.value.trim().replace(',', '');
            
            // 2. Converte para Capitalize Case antes de processar
            let valor = paraCapitalize(valorCru);
            
            // 3. Valida e adiciona
            if (valor !== "" && !listaDeItens.includes(valor)) {
                listaDeItens.push(valor);
                criarTag(valor);
                atualizarInputEscondido();
            }
            tagInput.value = ""; 
        }
    });

    // Evita o envio acidental do formulário ao apertar Enter
    tagInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') e.preventDefault();
    });

    // Cria a tag visual dentro do container atual
    function criarTag(texto) {
        const span = document.createElement('span');
        span.className = "badge bg-primary d-flex align-items-center gap-2 p-2 fs-6";
        
        const botaoFechar = document.createElement('button');
        botaoFechar.type = "button";
        botaoFechar.className = "btn-close btn-close-white";
        botaoFechar.style.fontSize = "0.6rem";
        
        botaoFechar.addEventListener('click', (evento) => {
            evento.stopPropagation();
            span.remove();
            listaDeItens = listaDeItens.filter(item => item !== texto);
            atualizarInputEscondido();
        });

        span.textContent = texto + " ";
        span.appendChild(botaoFechar);
        
        tagContainer.insertBefore(span, tagInput);
    }

    // Atualiza apenas o input hidden deste bloco
    function atualizarInputEscondido() {
        inputEscondido.value = listaDeItens.join(',');
    }
});

// Opção para readicionar nos inputs tags removidas
document.addEventListener('DOMContentLoaded', function () {
    function configurarGerenciadorTags(idRemovidos, idContainer, idInputHidden) {
        const containerRemovidos = document.getElementById(idRemovidos);
        const tagContainer = document.getElementById(idContainer);
        const inputEscondido = document.getElementById(idInputHidden);
        
        if (!tagContainer || !inputEscondido) return; // Validação caso o elemento não exista na página
        
        const tagInput = tagContainer.querySelector('.tag-input');

        // Atualiza a string separada por vírgula no input hidden correto
        function atualizarInputEscondido() {
            const tagsAtivas = [];
            tagContainer.querySelectorAll('.tag-predefinida').forEach(tag => {
                // Remove espaços e quebras de linha para pegar só o texto puro
                const texto = tag.textContent.replace(/[\n\r]+|[\s]{2,}/g, ' ').trim();
                if (texto) tagsAtivas.push(texto);
            });
            inputEscondido.value = tagsAtivas.join(',');
        }

        // Evento para READICIONAR quando clica no item removido
        if (containerRemovidos) {
            containerRemovidos.addEventListener('click', function (e) {
                const botaoReadicionar = e.target.closest('.btn-readicionar');
                
                if (botaoReadicionar) {
                    const nomeItem = botaoReadicionar.getAttribute('data-item');

                    // Cria a nova tag ativa
                    const novaTag = document.createElement('span');
                    novaTag.className = 'badge bg-primary d-flex align-items-center gap-2 p-2 fs-6 tag-predefinida';
                    novaTag.innerHTML = `
                        ${nomeItem}
                        <button type="button" class="btn-close btn-close-white btn-remover-predefinido" style="font-size: 0.6rem;" data-item="${nomeItem}"></button>
                    `;

                    // Insere visualmente antes do input de texto correspondente
                    tagContainer.insertBefore(novaTag, tagInput);

                    // Remove da lista de excluídos
                    botaoReadicionar.remove();

                    // Atualiza o input hidden respectivo
                    atualizarInputEscondido();
                }
            });
        }

        // Evento para REMOVER quando clica no 'X' da tag ativa
        tagContainer.addEventListener('click', function (e) {
            if (e.target.classList.contains('btn-remover-predefinido')) {
                const tagParaRemover = e.target.closest('.tag-predefinida');
                if (tagParaRemover) {
                    tagParaRemover.remove();
                    atualizarInputEscondido();
                }
            }
        });
    }

    // --- ATIVAÇÃO DOS GERENCIADORES ---
    configurarGerenciadorTags('removidos-servicos', 'container-servicos', 'input-servicos');

    configurarGerenciadorTags('removidos-roupas', 'container-roupas', 'input-roupas');

    configurarGerenciadorTags('removidos-tecidos', 'container-tecidos', 'input-tecidos');
});

// Opção para adicionar a tag removida para o container removidos
document.addEventListener('DOMContentLoaded', function () {
    function configurarRetornoRemovidos(idContainer, idRemovidos) {
        const tagContainer = document.getElementById(idContainer);
        const containerRemovidos = document.getElementById(idRemovidos);

        if (!tagContainer || !containerRemovidos) return;

        tagContainer.addEventListener('click', function (e) {
            if (e.target.classList.contains('btn-remover-predefinido')) {
                const nomeItem = e.target.getAttribute('data-item');

                if (nomeItem) {
                    const jaExiste = containerRemovidos.querySelector(`[data-item="${nomeItem}"]`);
                    if (jaExiste) return;

                    // NOVO: Se o container de removidos estava escondido pelo Django (d-none), nós o exibimos agora
                    if (containerRemovidos.classList.contains('d-none')) {
                        containerRemovidos.classList.remove('d-none');
                    }

                    const novoRemovido = document.createElement('span');
                    novoRemovido.className = 'badge bg-body-secondary text-secondary-emphasis border border-secondary-subtle px-2 py-1.5 rounded-pill shadow-sm transition-all opacity-75 btn-readicionar d-inline-flex align-items-center gap-2';
                    novoRemovido.style.cursor = 'pointer';
                    novoRemovido.setAttribute('title', 'Clique para adicionar novamente');
                    novoRemovido.setAttribute('data-item', nomeItem);

                    novoRemovido.innerHTML = `
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-repeat" viewBox="0 0 16 16">
                            <path d="M11.534 7h3.932a.25.25 0 0 1 .192.41l-1.966 2.36a.25.25 0 0 1-.384 0l-1.966-2.36a.25.25 0 0 1 .192-.41m-11 2h3.932a.25.25 0 0 0 .192-.41L2.692 6.23a.25.25 0 0 0-.384 0L.342 8.59A.25.25 0 0 0 .534 9"/>
                            <path fill-rule="evenodd" d="M8 3c-1.552 0-2.94.707-3.857 1.818a.5.5 0 1 1-.771-.636A6.002 6.002 0 0 1 13.917 7H12.9A5 5 0 0 0 8 3M3.1 9a5.002 5.002 0 0 0 8.757 2.182.5.5 0 1 1 .771.636A6.002 6.002 0 0 1 2.083 9z"/>
                        </svg>
                        ${nomeItem}
                    `;

                    containerRemovidos.appendChild(novoRemovido);
                }
            }
        }, true);
    }

    // --- ATIVAÇÃO DOS RETORNOS ---
    configurarRetornoRemovidos('container-servicos', 'removidos-servicos');
    configurarRetornoRemovidos('container-roupas', 'removidos-roupas');
    configurarRetornoRemovidos('container-tecidos', 'removidos-tecidos');
});

// Opção para esconder o container de removidos quando ele ficar totalmente vazio
document.addEventListener('DOMContentLoaded', function () {
    function monitorarContainerVazio(idRemovidos) {
        const containerRemovidos = document.getElementById(idRemovidos);
        if (!containerRemovidos) return;

        // Escuta cliques dentro do container de removidos
        containerRemovidos.addEventListener('click', function () {
            // Executa um milissegundo depois para dar tempo do badge ser removido da tela
            setTimeout(() => {
                // Conta quantos badges (.btn-readicionar) ainda restam lá dentro
                const restamBadges = containerRemovidos.querySelectorAll('.btn-readicionar').length;
                
                // Se não restar nenhum, esconde a div inteira (esconde o texto "Removidos:")
                if (restamBadges === 0) {
                    containerRemovidos.classList.add('d-none');
                }
            }, 50);
        });
    }

    // --- ATIVAÇÃO DO MONITORAMENTO ---
    monitorarContainerVazio('removidos-servicos');
    monitorarContainerVazio('removidos-roupas');
    monitorarContainerVazio('removidos-tecidos');
});
