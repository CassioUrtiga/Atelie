// Adicionar pedido com imagem
var idImg = 0;

let btAddImg = $('#addImg');
let novaImagem = $('#novaImagem');

btAddImg.on('click', function() {
    novaImagem.append(`
        <div id="bloco-imagem-${idImg}" class="mb-4 p-3 border rounded bg-light">
            <div class="mb-3 d-flex align-items-center gap-2">
                <input class="form-control input-imagem" type="file" accept="image/*" id="input-imagem-${idImg}" name="image" data-id="${idImg}">

                <button type="button" class="btn btn-danger" onclick="remover_imagem(${idImg})">
                    Remover
                </button>
            </div>
            <div id="preview-${idImg}" class="mb-3 text-center" style="display: none;">
                <img id="img-preview-${idImg}" src="" alt="Preview" class="img-fluid img-thumbnail" style="max-height: 200px;">
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

    if (input.files && input.files[0]) {
        const arquivo = input.files[0];

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
