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
