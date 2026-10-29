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

document.addEventListener('click', function(e) {
    
    let boton = e.target.closest('.btn-editar-usuario');
    if (boton) {
        document.getElementById('edit_id_usuario').value = boton.dataset.id;
        document.getElementById('edit_nombre').value = boton.dataset.nombre;
        document.getElementById('edit_apellido1').value = boton.dataset.ap1;
        document.getElementById('edit_apellido2').value = boton.dataset.ap2;
        document.getElementById('edit_correo').value = boton.dataset.correo;
        document.getElementById('edit_telefono').value = boton.dataset.tel;
        document.getElementById('edit_id_rol').value = boton.dataset.rol;
    }
});