// Adicionar pedido com imagem
var idImg = 0;

let btAddImg = $('#addImg');
let novaImagem = $('#novaImagem');

btAddImg.on('click', function() {
    novaImagem.append(`
        <div id="bloco-imagem-${idImg}" class="mb-3 p-3 border border-secondary-subtle rounded-3 bg-white shadow-sm position-relative animate__animated animate__fadeIn">
    
            <div class="row align-items-center g-2">
                <div class="col">
                    <div class="input-group">
                        <span class="input-group-text bg-light text-dark">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-upload" viewBox="0 0 16 16">
                                <path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5"/>
                                <path d="M7.646 1.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 2.707V11.5a.5.5 0 0 1-1 0V2.707L5.354 4.854a.5.5 0 1 1-.708-.708z"/>
                            </svg>
                        </span>
                        <input class="form-control input-imagem" type="file" accept="image/*" id="input-imagem-${idImg}" name="image" data-id="${idImg}">
                    </div>
                </div>
                
                <div class="col-auto">
                    <button type="button" class="btn btn-outline-danger d-flex align-items-center gap-1" onclick="remover_imagem(${idImg})" title="Remover Imagem">
                        <span class="d-none d-sm-inline">Remover</span>
                    </button>
                </div>
            </div>
            
            <div id="preview-${idImg}" class="mt-3 text-center border rounded bg-light p-2 position-relative visual-preview" style="display: none;">
                <p class="text-muted small mb-2 fw-medium">Pré-visualização</p>
                <img id="img-preview-${idImg}" src="" alt="Pré-visualização" class="img-fluid rounded shadow-sm border" style="max-height: 180px; object-fit: contain;">
            </div>
        </div>
    `);

    idImg += 1;
});

novaImagem.on('change', '.form-control[type="file"]', function() {
    const input = this;
    const id = $(input).data('id');
    const previewContainer = $(`#preview-${id}`);
    const previewImg = $(`#img-preview-${id}`);
    const previewText = $(`#preview-${id} p`);

    if (input.files && input.files[0]) {
        const arquivo = input.files[0];
        const limiteMaximo = 1024 * 1024; // 1 MB

        // Validação de tamanho
        if (arquivo.size > limiteMaximo) {
            $(`#preview-${id} p`).text("Tamanho máximo permitido 1 MB.");

            $(input).val(''); 
    
            previewImg.attr('src', '');
            previewContainer.show();
            return;
        }

        // Se a imagem for válida, reseta o texto do preview para o padrão
        previewText.text("Pré-visualização").removeClass('text-danger').addClass('text-muted');
        previewImg.show();

        const reader = new FileReader();

        reader.onload = function(e) {
            previewImg.attr('src', e.target.result);
            previewContainer.show();
        }

        reader.readAsDataURL(arquivo);
    } else {
        previewContainer.hide();
        previewImg.attr('src', '');
    }
});

function remover_imagem(id) {
    $(`#bloco-imagem-${id}`).remove();
}
