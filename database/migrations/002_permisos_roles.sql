-- 1. permisos

CREATE TABLE IF NOT EXISTS permisos (
    id_permiso   INT AUTO_INCREMENT PRIMARY KEY,
    codigo       VARCHAR(60) NOT NULL UNIQUE,
    nombre       VARCHAR(100) NOT NULL,
    descripcion  VARCHAR(180),
    modulo       VARCHAR(60) NOT NULL,
    orden        INT NOT NULL DEFAULT 0
) ENGINE=InnoDB;


-- ============================================================
-- 2. RELACION ENTRE ROLES Y PERMISOS
-- ============================================================

CREATE TABLE IF NOT EXISTS rol_permiso (
    id_rol       INT NOT NULL,
    id_permiso   INT NOT NULL,

    PRIMARY KEY (id_rol, id_permiso),

    CONSTRAINT fk_rol_permiso_rol
        FOREIGN KEY (id_rol)
        REFERENCES roles(id_rol)
        ON DELETE CASCADE,

    CONSTRAINT fk_rol_permiso_permiso
        FOREIGN KEY (id_permiso)
        REFERENCES permisos(id_permiso)
        ON DELETE CASCADE

) ENGINE=InnoDB;


-- ============================================================
-- 3. CATALOGO BASE DE PERMISOS
-- ============================================================

INSERT IGNORE INTO permisos
    (codigo, nombre, descripcion, modulo, orden)
VALUES

-- USUARIOS
(
    'usuarios.ver',
    'Consultar usuarios',
    'Permite consultar los usuarios registrados en el sistema.',
    'Usuarios',
    10
),

(
    'usuarios.crear',
    'Crear usuarios',
    'Permite registrar nuevos usuarios.',
    'Usuarios',
    20
),

(
    'usuarios.editar',
    'Editar usuarios',
    'Permite modificar la información de los usuarios.',
    'Usuarios',
    30
),

(
    'usuarios.eliminar',
    'Eliminar usuarios',
    'Permite eliminar usuarios del sistema.',
    'Usuarios',
    40
),


-- ROLES
(
    'roles.gestionar',
    'Gestionar roles',
    'Permite administrar roles y sus permisos.',
    'Roles',
    50
),


-- GRUPOS
(
    'grupos.ver',
    'Consultar grupos',
    'Permite consultar grupos y secciones.',
    'Grupos',
    60
),

(
    'grupos.crear',
    'Crear grupos',
    'Permite crear grupos y secciones.',
    'Grupos',
    70
),

(
    'grupos.editar',
    'Editar grupos',
    'Permite modificar grupos y secciones.',
    'Grupos',
    80
),

(
    'grupos.eliminar',
    'Eliminar grupos',
    'Permite eliminar grupos y secciones.',
    'Grupos',
    90
),


-- ASISTENCIA
(
    'asistencia.consultar',
    'Consultar asistencia',
    'Permite consultar registros de asistencia.',
    'Asistencia',
    100
),

(
    'asistencia.gestionar',
    'Gestionar asistencia',
    'Permite registrar y modificar asistencia.',
    'Asistencia',
    110
),


-- TAREAS
(
    'tareas.consultar',
    'Consultar tareas',
    'Permite consultar tareas académicas.',
    'Tareas',
    120
),

(
    'tareas.gestionar',
    'Gestionar tareas',
    'Permite publicar, editar y eliminar tareas.',
    'Tareas',
    130
),


-- CALIFICACIONES
(
    'calificaciones.consultar',
    'Consultar calificaciones',
    'Permite consultar calificaciones académicas.',
    'Calificaciones',
    140
),

(
    'calificaciones.gestionar',
    'Gestionar calificaciones',
    'Permite registrar y modificar calificaciones.',
    'Calificaciones',
    150
),


-- COMUNICADOS
(
    'comunicados.consultar',
    'Consultar comunicados',
    'Permite consultar comunicados institucionales.',
    'Comunicados',
    160
),

(
    'comunicados.gestionar',
    'Gestionar comunicados',
    'Permite crear y administrar comunicados.',
    'Comunicados',
    170
),


-- CALENDARIO
(
    'calendario.consultar',
    'Consultar calendario',
    'Permite consultar eventos del calendario.',
    'Calendario',
    180
),

(
    'calendario.gestionar',
    'Gestionar calendario',
    'Permite crear y administrar eventos.',
    'Calendario',
    190
),


-- REPORTES
(
    'reportes.consultar',
    'Consultar reportes',
    'Permite consultar reportes institucionales.',
    'Reportes',
    200
),

(
    'reportes.exportar',
    'Exportar reportes',
    'Permite exportar reportes institucionales.',
    'Reportes',
    210
);


-- ============================================================
-- 4. ADMINISTRADOR = ACCESO TOTAL
-- ============================================================

INSERT IGNORE INTO rol_permiso (id_rol, id_permiso)
SELECT
    r.id_rol,
    p.id_permiso
FROM roles r
CROSS JOIN permisos p
WHERE r.nombre = 'Administrador';


-- ============================================================
-- 5. DOCENTE
-- ============================================================

INSERT IGNORE INTO rol_permiso (id_rol, id_permiso)
SELECT
    r.id_rol,
    p.id_permiso
FROM roles r
JOIN permisos p
WHERE r.nombre = 'Docente'
AND p.codigo IN (
    'grupos.ver',
    'asistencia.consultar',
    'asistencia.gestionar',
    'tareas.consultar',
    'tareas.gestionar',
    'calificaciones.consultar',
    'calificaciones.gestionar',
    'comunicados.consultar',
    'comunicados.gestionar',
    'calendario.consultar'
);


-- ============================================================
-- 6. ESTUDIANTE
-- ============================================================

INSERT IGNORE INTO rol_permiso (id_rol, id_permiso)
SELECT
    r.id_rol,
    p.id_permiso
FROM roles r
JOIN permisos p
WHERE r.nombre = 'Estudiante'
AND p.codigo IN (
    'asistencia.consultar',
    'tareas.consultar',
    'calificaciones.consultar',
    'comunicados.consultar',
    'calendario.consultar'
);


-- ============================================================
-- 7. PADRE DE FAMILIA
-- ============================================================

INSERT IGNORE INTO rol_permiso (id_rol, id_permiso)
SELECT
    r.id_rol,
    p.id_permiso
FROM roles r
JOIN permisos p
WHERE r.nombre = 'Padre de Familia'
AND p.codigo IN (
    'asistencia.consultar',
    'tareas.consultar',
    'calificaciones.consultar',
    'comunicados.consultar',
    'calendario.consultar'
);


-- ============================================================
-- 8. PERSONAL ADMINISTRATIVO
-- ============================================================

INSERT IGNORE INTO rol_permiso (id_rol, id_permiso)
SELECT
    r.id_rol,
    p.id_permiso
FROM roles r
JOIN permisos p
WHERE r.nombre = 'Personal Administrativo'
AND p.codigo IN (
    'usuarios.ver',
    'grupos.ver',
    'comunicados.consultar',
    'calendario.consultar',
    'reportes.consultar',
    'reportes.exportar'
);