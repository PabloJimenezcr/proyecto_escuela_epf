-- Agregar sección al grupo
ALTER TABLE grupos
ADD COLUMN seccion VARCHAR(10) NOT NULL
DEFAULT 'A'
AFTER nivel;


-- Un mismo nivel, sección y año lectivo no puede existir dos veces

ALTER TABLE grupos
ADD CONSTRAINT uq_grupo_nivel_seccion_anio
UNIQUE (
    nivel,
    seccion,
    anio_lectivo
);