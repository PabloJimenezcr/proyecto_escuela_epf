╔══════════════════════════════════════════════════════════════════════════════╗
║ ║ ║ ESCUELA ENRIQUE PINTO FERNÁNDEZ ║ ║ Sistema Web Institucional ║ ║
║ ║ Educación que transforma • Futuro que construimos ║ ║ ║
╚══════════════════════════════════════════════════════════════════════════════╝

📚 SOBRE EL PROYECTO
══════════════════════════════════════════════════════════════════════════════

Este proyecto corresponde al desarrollo de un sistema web institucional
para la Escuela Enrique Pinto Fernández.

La propuesta busca construir una experiencia digital moderna,
profesional y visualmente atractiva que represente la identidad de la
institución y permita presentar información relevante de la escuela de
una manera clara, ordenada y accesible.

El proyecto está siendo desarrollado con tecnologías web fundamentales,
manteniendo una estructura modular y organizada para facilitar su
evolución.

🎯 OBJETIVO
══════════════════════════════════════════════════════════════════════════════

Crear una plataforma web institucional que combine:

• Identidad visual moderna. • Experiencia de usuario atractiva. •
Información institucional organizada. • Navegación sencilla e intuitiva.
• Diseño responsive. • Código estructurado y mantenible. • Una
experiencia de entrada memorable mediante un loader animado.

✨ EXPERIENCIA VISUAL
══════════════════════════════════════════════════════════════════════════════

Uno de los objetivos principales del proyecto es que la plataforma no se
perciba como un sitio web institucional tradicional, sino como una
experiencia digital moderna.

La página de inicio incorpora una pantalla de carga inicial diseñada
para presentar la identidad de la Escuela Enrique Pinto Fernández antes
de mostrar el contenido principal.

El loader incluye:

• Identidad institucional. • Iconografía educativa. • Animaciones
suaves. • Efectos de iluminación. • Fondo con profundidad visual. •
Indicador de carga animado. • Transición progresiva hacia el contenido
principal.

La intención es generar desde el primer segundo una sensación de
calidad, cuidado y profesionalismo.

🖥️ PANTALLAS PRINCIPALES
══════════════════════════════════════════════════════════════════════════════

Actualmente la estructura contempla las siguientes pantallas:

1.  INICIO Página principal de la institución.

    Incluye una propuesta visual orientada a comunicar: • Identidad
    institucional. • Mensaje principal. • Información sobre la escuela.
    • Misión. • Programas. • Valores. • Accesos de navegación. •
    Llamados a la acción.

2.  INICIO DE SESIÓN Pantalla destinada al acceso al sistema
    institucional.

    La interfaz mantiene la misma línea visual del sitio para conseguir
    una experiencia coherente entre la página pública y el sistema.

🎨 IDENTIDAD VISUAL
══════════════════════════════════════════════════════════════════════════════

La interfaz utiliza una línea gráfica institucional basada
principalmente en tonos oscuros y azules profundos, complementados con
un color dorado/ amarillo para destacar elementos importantes.

La combinación busca transmitir:

• Confianza. • Educación. • Profesionalismo. • Innovación. • Modernidad.
• Cercanía.

La tipografía principal utiliza Google Fonts, incluyendo Montserrat para
reforzar los títulos y elementos destacados, acompañada por una
tipografía legible para los textos de interfaz.

🧩 TECNOLOGÍAS UTILIZADAS
══════════════════════════════════════════════════════════════════════════════

HTML5 Estructura semántica y organización del contenido.

CSS / SASS Desarrollo de estilos mediante una arquitectura modular y
reutilizable.

JavaScript Interacciones, comportamiento dinámico y control de la
experiencia de carga de la plataforma.

Bootstrap Sistema de componentes y estructura responsive.

Remix Icon Biblioteca de iconos utilizada para reforzar la interfaz
visual.

Google Fonts Tipografías utilizadas para construir una identidad visual
consistente.

📁 ESTRUCTURA DEL PROYECTO
══════════════════════════════════════════════════════════════════════════════

proyectoEscuela/ │ ├── css/ │ ├── img/ │ ├── js/ │ ├── login.js │ └──
main.js │ ├── sass/ │ ├── _base.scss │ ├── _home.scss │ ├── _loader.scss
│ ├── _login.scss │ ├── _mixins.scss │ ├── _navbar.scss │ ├──
_variables.scss │ ├── style.scss │ └── style.css │ ├── index.html └──
login.html

🏗️ ARQUITECTURA SASS
══════════════════════════════════════════════════════════════════════════════

El proyecto utiliza una arquitectura modular para separar las diferentes
responsabilidades de los estilos.

_variables.scss Variables globales de colores, tipografías, tamaños y
otros valores.

_mixins.scss Mixins reutilizables para evitar duplicación de estilos.

_base.scss Estilos generales y reglas base de la aplicación.

_navbar.scss Estilos correspondientes a la navegación principal.

_home.scss Estilos específicos de la página de inicio.

_loader.scss Estilos, efectos y animaciones de la pantalla de carga.

_login.scss Estilos correspondientes a la pantalla de inicio de sesión.

style.scss Archivo principal que importa y centraliza los módulos SASS.

style.css Archivo CSS generado a partir del SASS.

⚙️ FLUJO DE TRABAJO SASS
══════════════════════════════════════════════════════════════════════════════

El desarrollo de estilos se realiza directamente sobre los archivos
.scss.

El flujo de trabajo es:

    Archivos SCSS
         │
         ▼
    style.scss
         │
         ▼
    Live Sass Compiler
         │
         ▼
    style.css
         │
         ▼
    HTML

🚀 EXPERIENCIA DEL LOADER
══════════════════════════════════════════════════════════════════════════════

Al ingresar a la página principal, el contenido permanece oculto
mientras se presenta la experiencia inicial de carga.

El flujo es:

    Usuario abre index.html
             │
             ▼
       Loader institucional
             │
             ▼
       Animaciones visuales
             │
             ▼
       Carga de la página
             │
             ▼
       Transición del loader
             │
             ▼
       Contenido principal

El comportamiento del loader se controla mediante JavaScript y las
transiciones visuales se desarrollan con SASS.

💡 PRINCIPIOS DEL PROYECTO
══════════════════════════════════════════════════════════════════════════════

El desarrollo busca mantener los siguientes principios:

✓ Diseño centrado en la experiencia del usuario. ✓ Interfaz moderna y
profesional. ✓ Código organizado y modular. ✓ Separación de
responsabilidades. ✓ Diseño responsive. ✓ Componentes visuales
consistentes. ✓ Animaciones utilizadas con propósito. ✓ Identidad
institucional presente en toda la experiencia.

🧑‍💻 DESARROLLO
══════════════════════════════════════════════════════════════════════════════

Proyecto institucional Escuela Enrique Pinto Fernández

Tecnologías: HTML5 • SASS • JavaScript • Bootstrap • Remix Icon • Google
Fonts

📌 ESTADO DEL PROYECTO
══════════════════════════════════════════════════════════════════════════════

🚧 En desarrollo.

La plataforma se encuentra en proceso de construcción. La estructura
base, la identidad visual, la página de inicio, el sistema de estilos
modular y la experiencia inicial de carga forman parte de la base actual
del proyecto.

Nuevas funcionalidades y pantallas serán incorporadas progresivamente.

══════════════════════════════════════════════════════════════════════════════

                 ESCUELA ENRIQUE PINTO FERNÁNDEZ

              "Construimos el futuro desde hoy."

══════════════════════════════════════════════════════════════════════════════
