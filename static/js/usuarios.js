document.getElementById('buscadorUsuarios').addEventListener('keyup', function() {
    let filtro = this.value.toLowerCase();
    let filas = document.querySelectorAll('.usuario-fila');

    filas.forEach(function(fila) {
        let textoFila = fila.textContent.toLowerCase();
        if (textoFila.includes(filtro)) {
            fila.style.display = '';
        } else {
            fila.style.display = 'none';
        }
    });
});