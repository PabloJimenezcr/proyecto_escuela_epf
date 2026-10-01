-- Identifica si el rol pertenece al sistema o si fue creado posteriormente por un administrador
ALTER TABLE roles
ADD COLUMN es_sistema TINYINT(1) NOT NULL DEFAULT 0
AFTER descripcion;

-- Los cinco perfiles originales de la plataforma son roles protegidos del sistema
UPDATE roles
SET es_sistema = 1
WHERE nombre IN (
    'Administrador',
    'Docente',
    'Estudiante',
    'Padre de Familia',
    'Personal Administrativo'
);