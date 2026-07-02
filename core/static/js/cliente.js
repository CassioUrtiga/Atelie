// Formulário adicionar pedido com imagem
var instancesCroppie = {};
var idImg = 0;

let btAddImg = $('#addImg');
let novaImagem = $('#novaImagem');

btAddImg.on('click', function() {
    novaImagem.append(`
        <div id="bloco-imagem-${idImg}">
            <div class="mb-3">
                <h3>Imagem</h3>
                <input class="form-control" type="file" accept="image/jpeg" id="imagem-crop-${idImg}">
                <input type="hidden" name="image" id="base64-imagem-${idImg}">
            </div>
            <div id="preview-${idImg}"></div>
            <div class="text-center">
                <button type="button" class="btn btn-danger btn-lg" onclick="remover_imagem(${idImg})">
                    Remover imagem
                </button>
            </div>
        </div>
    `);

    renderizarImagem(idImg);
    idImg += 1;
});

$('#formularioPedido').on('submit', function(e) {
    e.preventDefault();
    
    let form = this;
    let promessas = [];

    Object.keys(instancesCroppie).forEach(function(id) {
        if (instancesCroppie[id]) {
            let promisesCroppie = instancesCroppie[id].croppie('result', {
                type: 'base64',
                size: 'viewport',
                format: 'jpeg'
            }).then(function(base64Resultado) {
                $(`#base64-imagem-${id}`).val(base64Resultado);
            });
            
            promessas.push(promisesCroppie);
        }
    });

    Promise.all(promessas).then(function() {
        form.submit(); 
    });
});

function renderizarImagem(id) {

    instancesCroppie[id] = $(`#preview-${id}`).croppie({
        enableExif: true,
        enableOrientation: true,
        mouseWheelZoom: false,

        viewport: { width: 650, height: 400, type: 'square'},
        boundary: { width: 750, height: 450},
    });

    $(`#imagem-crop-${id}`).off('change').on('change', function(event) {
        let reader = new FileReader();

        reader.onload = function(e) {
            instancesCroppie[id].croppie('bind', {
                url: e.target.result
            });
        };
        
        if (event.target.files[0]) {
            reader.readAsDataURL(event.target.files[0]);
        }
    });
}

function remover_imagem(id) {
    $(`#bloco-imagem-${id}`).remove();
    
    if (instancesCroppie[id]) {
        instancesCroppie[id].croppie('destroy');
        delete instancesCroppie[id];
    }
}
