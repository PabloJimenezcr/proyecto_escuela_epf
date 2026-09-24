-- ============================================
-- Sistema De Gestión Escolar - Escuela Enrique Pinto Fernández
--
-- 11 módulos 1Roles,2Administración Institucional, 3Administracion de Usuarios, 4Gestión de Estudiantes, 5Gestion de Docentes,
-- 6Asistencia, 7Tareas, 8Calificaciones, 9Comunicados, 10Consulta de Padres, 11Calendario
-- =======================================

CREATE DATABASE epf_sistema_escolar
CHARACTER SET utf8mb4
COLLATE utf8mb4_spanish_ci;
USE epf_sistema_escolar;

-- ============================================================================
-- M-01: ROLES Y AUTENTICACIÓN
-- ============================================================================

-- Catálogo de roles del sistema - administrador define los roles

CREATE TABLE roles (
    id_rol      INT AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(40) NOT NULL UNIQUE,
    descripcion VARCHAR(150)
) ENGINE=InnoDB;

-- Tabla base de todo usuario que se rgiste: Como el login, logout, recupersr password
-- Perfiels como administrador, docente, estudiante, padre, personal administrativo

CREATE TABLE usuarios (
    id_usuario      INT AUTO_INCREMENT PRIMARY KEY,
    nombre          VARCHAR(60) NOT NULL,
    apellido1       VARCHAR(60) NOT NULL,
    apellido2       VARCHAR(60),
    correo          VARCHAR(120) NOT NULL UNIQUE,
    contrasena_hash VARCHAR(255) NOT NULL,
    telefono        VARCHAR(20),
    id_rol          INT NOT NULL,
    estado          ENUM('activo','inactivo') NOT NULL DEFAULT 'activo',
    fecha_registro  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_usuarios_rol FOREIGN KEY (id_rol) REFERENCES roles(id_rol)
) ENGINE=InnoDB;

-- Tokens de recuperacion de pass

CREATE TABLE recuperacion_contrasena (
    id_recuperacion INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario      INT NOT NULL,
    token           VARCHAR(100) NOT NULL UNIQUE,
    fecha_solicitud DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_expira    DATETIME NOT NULL,
    utilizado       TINYINT(1) NOT NULL DEFAULT 0,
    CONSTRAINT fk_recuperacion_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- M-02: ADMINISTRACIÓN INSTITUCIONAL (GRUPOS Y SECCIONES)
-- ============================================================================

-- crud y consultar grupos

CREATE TABLE grupos (
    id_grupo        INT AUTO_INCREMENT PRIMARY KEY,
    nombre          VARCHAR(10) NOT NULL UNIQUE,   
    nivel           VARCHAR(30) NOT NULL,           
    anio_lectivo    YEAR NOT NULL,
    id_docente_guia INT NULL,                       
    fecha_creacion  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Catálogos de materias, usado por diocentes, tareas y calificaciones

CREATE TABLE materias (
    id_materia INT AUTO_INCREMENT PRIMARY KEY,
    nombre     VARCHAR(60) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- Catálogo de periodos académicos, usado por calificaciones
CREATE TABLE periodos_academicos (
    id_periodo   INT AUTO_INCREMENT PRIMARY KEY,
    nombre       VARCHAR(40) NOT NULL,   -- ej. 'I Periodo 2026'
    fecha_inicio DATE NOT NULL,
    fecha_fin    DATE NOT NULL,
    anio_lectivo YEAR NOT NULL
) ENGINE=InnoDB;

-- ============================================================================
-- M-04: GESTIÓN DE ESTUDIANTES
-- ============================================================================

-- registrar estudiante con datos personales, fecha de nacimiento y grupo asignado
-- el estudiante consulta/actualiza su propio perfil se hace sobre 'usuarios'
CREATE TABLE estudiantes (
    id_estudiante     INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario        INT NOT NULL UNIQUE,
    fecha_nacimiento  DATE NOT NULL,
    id_grupo          INT NOT NULL,
    fecha_matricula   DATE NOT NULL DEFAULT (CURRENT_DATE),
    CONSTRAINT fk_estudiantes_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    CONSTRAINT fk_estudiantes_grupo   FOREIGN KEY (id_grupo)   REFERENCES grupos(id_grupo)
) ENGINE=InnoDB;

-- ============================================================================
-- M-05: GESTIÓN DE DOCENTES
-- ============================================================================

-- registrar docente - docente consulta y actualiza su perfil
CREATE TABLE docentes (
    id_docente     INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario     INT NOT NULL UNIQUE,
    especialidad   VARCHAR(80),
    fecha_ingreso  DATE NOT NULL DEFAULT (CURRENT_DATE),
    CONSTRAINT fk_docentes_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB;
-- Ahora que 'docentes' existe, se agrega la llave foránea pendiente en 'grupos'
-- asignar docente guia a un grup
ALTER TABLE grupos
  ADD CONSTRAINT fk_grupos_docente_guia FOREIGN KEY (id_docente_guia) REFERENCES docentes(id_docente);

-- asignación de materias/grupos a cada docente 
CREATE TABLE docente_materia_grupo (
    id_asignacion INT AUTO_INCREMENT PRIMARY KEY,
    id_docente    INT NOT NULL,
    id_materia    INT NOT NULL,
    id_grupo      INT NOT NULL,
    CONSTRAINT fk_dmg_docente FOREIGN KEY (id_docente) REFERENCES docentes(id_docente) ON DELETE CASCADE,
    CONSTRAINT fk_dmg_materia FOREIGN KEY (id_materia) REFERENCES materias(id_materia),
    CONSTRAINT fk_dmg_grupo   FOREIGN KEY (id_grupo)   REFERENCES grupos(id_grupo),
    CONSTRAINT uq_docente_materia_grupo UNIQUE (id_docente, id_materia, id_grupo)
) ENGINE=InnoDB;

-- ============================================================================
-- M-03: ADMINISTRACIÓN DE USUARIOS (PADRES, PERSONAL ADMINISTRATIVO, VINCULACIÓN), se combina padres aquí y no tabla indivisual como el M10
-- ============================================================================
-- Registro de apdresd de familiac on sus datos 
CREATE TABLE padres (
    id_padre    INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario  INT NOT NULL UNIQUE,
    CONSTRAINT fk_padres_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB;

-- vinculación de padre de familia a estudiante
CREATE TABLE padre_estudiante (
    id_vinculo    INT AUTO_INCREMENT PRIMARY KEY,
    id_padre      INT NOT NULL,
    id_estudiante INT NOT NULL,
    parentesco    VARCHAR(30) DEFAULT 'Encargado',
    CONSTRAINT fk_pe_padre      FOREIGN KEY (id_padre)      REFERENCES padres(id_padre) ON DELETE CASCADE,
    CONSTRAINT fk_pe_estudiante FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante) ON DELETE CASCADE,
    CONSTRAINT uq_padre_estudiante UNIQUE (id_padre, id_estudiante)
) ENGINE=InnoDB;

-- personal administrativo
CREATE TABLE personal_administrativo (
    id_administrativo INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario        INT NOT NULL UNIQUE,
    cargo             VARCHAR(60),
    CONSTRAINT fk_administrativo_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- M-06: ASISTENCIA
-- ============================================================================

-- registrar, consultar y modificar asistencia diaria
CREATE TABLE asistencia (
    id_asistencia   INT AUTO_INCREMENT PRIMARY KEY,
    id_estudiante   INT NOT NULL,
    id_grupo        INT NOT NULL,
    id_docente      INT NOT NULL,       -- quien registró el dato
    fecha           DATE NOT NULL,
    estado          ENUM('presente','ausente','tardia','justificada') NOT NULL,
    observacion     VARCHAR(200),
    fecha_registro  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_asistencia_estudiante FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante) ON DELETE CASCADE,
    CONSTRAINT fk_asistencia_grupo      FOREIGN KEY (id_grupo)      REFERENCES grupos(id_grupo),
    CONSTRAINT fk_asistencia_docente    FOREIGN KEY (id_docente)    REFERENCES docentes(id_docente),
    CONSTRAINT uq_asistencia_dia UNIQUE (id_estudiante, fecha)
) ENGINE=InnoDB;

-- ============================================================================
-- M-07: TAREAS
-- ============================================================================

-- publicar, editar o eliminar tareas
CREATE TABLE tareas (
    id_tarea          INT AUTO_INCREMENT PRIMARY KEY,
    id_docente        INT NOT NULL,
    id_grupo          INT NOT NULL,
    id_materia        INT NOT NULL,
    titulo            VARCHAR(150) NOT NULL,
    descripcion       TEXT,
    fecha_publicacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_entrega     DATE NOT NULL,
    CONSTRAINT fk_tareas_docente FOREIGN KEY (id_docente) REFERENCES docentes(id_docente) ON DELETE CASCADE,
    CONSTRAINT fk_tareas_grupo   FOREIGN KEY (id_grupo)   REFERENCES grupos(id_grupo),
    CONSTRAINT fk_tareas_materia FOREIGN KEY (id_materia) REFERENCES materias(id_materia)
) ENGINE=InnoDB;

-- registrar qué estudiantes han consultado una tarea publicada
CREATE TABLE tarea_consulta (
    id_consulta     INT AUTO_INCREMENT PRIMARY KEY,
    id_tarea        INT NOT NULL,
    id_estudiante   INT NOT NULL,
    fecha_consulta  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_tc_tarea      FOREIGN KEY (id_tarea)      REFERENCES tareas(id_tarea) ON DELETE CASCADE,
    CONSTRAINT fk_tc_estudiante FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante) ON DELETE CASCADE,
    CONSTRAINT uq_tarea_estudiante UNIQUE (id_tarea, id_estudiante)
) ENGINE=InnoDB;

-- ============================================================================
-- M-08: CALIFICACIONES
-- ============================================================================

-- ingresar y editar calificaciones por materia y periodo
CREATE TABLE calificaciones (
    id_calificacion INT AUTO_INCREMENT PRIMARY KEY,
    id_estudiante   INT NOT NULL,
    id_materia      INT NOT NULL,
    id_docente      INT NOT NULL,
    id_periodo      INT NOT NULL,
    nota            DECIMAL(5,2) NOT NULL CHECK (nota >= 0 AND nota <= 100),
    fecha_registro  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_calif_estudiante FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id_estudiante) ON DELETE CASCADE,
    CONSTRAINT fk_calif_materia    FOREIGN KEY (id_materia)    REFERENCES materias(id_materia),
    CONSTRAINT fk_calif_docente    FOREIGN KEY (id_docente)    REFERENCES docentes(id_docente),
    CONSTRAINT fk_calif_periodo    FOREIGN KEY (id_periodo)    REFERENCES periodos_academicos(id_periodo),
    CONSTRAINT uq_calificacion UNIQUE (id_estudiante, id_materia, id_periodo)
) ENGINE=InnoDB;

-- ============================================================================
-- M-09: COMUNICADOS
-- ============================================================================

-- administrador o docente crean y envían comunicados
CREATE TABLE comunicados (
    id_comunicado   INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario_emisor INT NOT NULL,
    titulo          VARCHAR(150) NOT NULL,
    contenido       TEXT NOT NULL,
    alcance         ENUM('institucional','grupo') NOT NULL,
    id_grupo        INT NULL,               -- NULL cuando alcance = 'institucional'
    fecha_envio     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_comunicados_emisor FOREIGN KEY (id_usuario_emisor) REFERENCES usuarios(id_usuario),
    CONSTRAINT fk_comunicados_grupo  FOREIGN KEY (id_grupo)          REFERENCES grupos(id_grupo)
) ENGINE=InnoDB;

-- registro de destintarios y su lectura, el padre visualiza comunicados
-- permite reconstruir el historial de a quién llegó cada comunicado
CREATE TABLE comunicado_destinatario (
    id_destinatario INT AUTO_INCREMENT PRIMARY KEY,
    id_comunicado   INT NOT NULL,
    id_padre        INT NOT NULL,
    leido           TINYINT(1) NOT NULL DEFAULT 0,
    fecha_lectura   DATETIME NULL,
    CONSTRAINT fk_cd_comunicado FOREIGN KEY (id_comunicado) REFERENCES comunicados(id_comunicado) ON DELETE CASCADE,
    CONSTRAINT fk_cd_padre      FOREIGN KEY (id_padre)      REFERENCES padres(id_padre) ON DELETE CASCADE,
    CONSTRAINT uq_comunicado_padre UNIQUE (id_comunicado, id_padre)
) ENGINE=InnoDB;

-- ============================================================================
-- M-11: CALENDARIO
-- ============================================================================

-- crear/editar eventos institucionales o de un grupo específico
CREATE TABLE eventos_calendario (
    id_evento       INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario_creador INT NOT NULL,
    titulo          VARCHAR(150) NOT NULL,
    descripcion     VARCHAR(300),
    fecha           DATE NOT NULL,
    alcance         ENUM('institucional','grupo') NOT NULL,
    id_grupo        INT NULL,               
    fecha_creacion  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_eventos_creador FOREIGN KEY (id_usuario_creador) REFERENCES usuarios(id_usuario),
    CONSTRAINT fk_eventos_grupo   FOREIGN KEY (id_grupo)           REFERENCES grupos(id_grupo)
) ENGINE=InnoDB;

-- ============================================================================
-- ÍNDICES ADICIONALES DE RENDIMIENTO
-- (consultas frecuentes: por grupo, por estudiante y por fecha)
-- ============================================================================
CREATE INDEX idx_asistencia_grupo_fecha ON asistencia(id_grupo, fecha);
CREATE INDEX idx_calif_estudiante       ON calificaciones(id_estudiante);
CREATE INDEX idx_tareas_grupo           ON tareas(id_grupo);
CREATE INDEX idx_eventos_fecha          ON eventos_calendario(fecha);
CREATE INDEX idx_usuarios_correo        ON usuarios(correo);

-- ================
-- DATOS BASE 
-- =================

INSERT INTO roles (nombre, descripcion) VALUES
('Administrador',            'Gestiona usuarios, grupos, reportes y configuración del sistema'),
('Docente',                   'Gestiona asistencia, tareas, calificaciones y comunicados de sus grupos'),
('Estudiante',                 'Consulta su información académica'),
('Padre de Familia',           'Consulta la información académica de sus hijos'),
('Personal Administrativo',    'Accede a funciones administrativas autorizadas por la institución');

INSERT INTO materias (nombre) VALUES
('Matemática'), ('Español'), ('Ciencias'), ('Estudios Sociales'),
('Inglés'), ('Educación Física'), ('Educación Cívica'), ('Artes Plásticas'), ('Música');

INSERT INTO periodos_academicos (nombre, fecha_inicio, fecha_fin, anio_lectivo) VALUES
('I Periodo 2026',  '2026-02-01', '2026-05-31', 2026),
('II Periodo 2026', '2026-06-01', '2026-09-30', 2026),
('III Periodo 2026','2026-10-01', '2026-12-15', 2026);



