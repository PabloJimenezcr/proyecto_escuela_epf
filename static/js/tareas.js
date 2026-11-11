// Procesar select de creación
document.getElementById('selectAsignacion').addEventListener('change', function() {
    if (this.value) {
        let valores = this.value.split('-');
        document.getElementById('hidden_materia').value = valores[0];
        document.getElementById('hidden_grupo').value = valores[1];
    }
});

//Buscador interactivo en tiempo real
document.getElementById('buscadorTareas').addEventListener('keyup', function() {
    let filtro = this.value.toLowerCase();
    let filas = document.querySelectorAll('.tarea-fila');
    filas.forEach(function(fila) {
        if (fila.textContent.toLowerCase().includes(filtro)) {
            fila.style.display = '';
        } else {
            fila.style.display = 'none';
        }
    });
});

// Jalar datos automáticamente a la modal al dar clic al lápiz
document.addEventListener('click', function(e) {
    let boton = e.target.closest('[data-bs-target="#modalEditarTarea"]');
    if (boton) {
        document.getElementById('edit_id_tarea').value = boton.dataset.id;
        document.getElementById('edit_titulo').value = boton.dataset.titulo;
        document.getElementById('edit_descripcion').value = boton.dataset.desc;
        document.getElementById('edit_fecha_entrega').value = boton.dataset.fecha;
        
        let select = document.getElementById('edit_selectAsignacion');
        select.value = boton.dataset.asignacion;
        
        let valores = boton.dataset.asignacion.split('-');
        document.getElementById('edit_hidden_materia').value = valores[0];
        document.getElementById('edit_hidden_grupo').value = valores[1];
    }
});

// Procesar select de edición
document.getElementById('edit_selectAsignacion').addEventListener('change', function() {
    if (this.value) {
        let valores = this.value.split('-');
        document.getElementById('edit_hidden_materia').value = valores[0];
        document.getElementById('edit_hidden_grupo').value = valores[1];
    }
});