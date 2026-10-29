CREATE TABLE IF NOT EXISTS asistencias (
    id_asistencia INT NOT NULL AUTO_INCREMENT,
    id_estudiante INT NOT NULL,
    fecha DATE NOT NULL,
    estado ENUM(
        'presente',
        'ausente',
        'tardanza',
        'justificado'
    ) NOT NULL,
    observacion VARCHAR(500) NULL,
    registrado_por INT NULL,
    fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME NULL DEFAULT NULL
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id_asistencia),

    UNIQUE KEY uq_asistencia_estudiante_fecha (
        id_estudiante,
        fecha
    ),

    KEY idx_asistencias_fecha (fecha),

    CONSTRAINT fk_asistencias_estudiante
        FOREIGN KEY (id_estudiante)
        REFERENCES estudiantes (id_estudiante)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_asistencias_usuario
        FOREIGN KEY (registrado_por)
        REFERENCES usuarios (id_usuario)
        ON UPDATE CASCADE
        ON DELETE SET NULL

) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci;


INSERT INTO permisos (
    codigo,
    nombre,
    descripcion,
    modulo,
    orden
)
VALUES
(
    'asistencia.registrar',
    'Registrar asistencia',
    'Permite registrar la asistencia diaria de un grupo',
    'Asistencia',
    10
),
(
    'asistencia.consultar',
    'Consultar historial de asistencia',
    'Permite consultar el historial individual de asistencia',
    'Asistencia',
    20
),
(
    'asistencia.editar',
    'Modificar registros de asistencia',
    'Permite modificar registros existentes de asistencia',
    'Asistencia',
    30
)
ON DUPLICATE KEY UPDATE
    nombre = VALUES(nombre),
    descripcion = VALUES(descripcion),
    modulo = VALUES(modulo),
    orden = VALUES(orden);


INSERT IGNORE INTO rol_permiso (
    id_rol,
    id_permiso
)
SELECT
    r.id_rol,
    p.id_permiso
FROM roles r
INNER JOIN permisos p
    ON p.codigo IN (
        'asistencia.registrar',
        'asistencia.consultar',
        'asistencia.editar'
    )
WHERE r.nombre = 'Docente';