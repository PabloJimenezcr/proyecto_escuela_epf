-- tabla de tareas entregadas por los estudiantes

CREATE TABLE IF NOT EXISTS tarea_entregas (
    id_entrega INT AUTO_INCREMENT PRIMARY KEY,
    id_tarea INT NOT NULL,
    id_estudiante INT NOT NULL,
    archivo_ruta VARCHAR(255) NOT NULL,
    texto_entrega TEXT,
    fecha_entrega TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_tarea) REFERENCES tareas(id_tarea) ON DELETE CASCADE,
    FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante) ON DELETE CASCADE,
    CONSTRAINT uq_entrega_unica UNIQUE (id_tarea, id_estudiante)
) ENGINE=InnoDB;