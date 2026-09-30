document.addEventListener("DOMContentLoaded", () => {

    const menuButton = document.getElementById("mobileMenuButton");
    const closeButton = document.getElementById("sidebarClose");
    const sidebar = document.getElementById("adminSidebar");
    const overlay = document.getElementById("sidebarOverlay");


    if (!menuButton || !sidebar || !overlay) {
        return;
    }


    const openSidebar = () => {

        sidebar.classList.add("is-open");
        overlay.classList.add("is-visible");

        document.body.style.overflow = "hidden";
    };


    const closeSidebar = () => {

        sidebar.classList.remove("is-open");
        overlay.classList.remove("is-visible");

        document.body.style.overflow = "";
    };


    menuButton.addEventListener("click", openSidebar);


    if (closeButton) {
        closeButton.addEventListener("click", closeSidebar);
    }


    overlay.addEventListener("click", closeSidebar);


    // Cerrar el sidebar cuando se selecciona una navegación
    // en dispositivos móviles.
    sidebar.querySelectorAll("a").forEach(link => {

        link.addEventListener("click", () => {

            if (window.innerWidth <= 991.98) {
                closeSidebar();
            }

        });

    });


    // Si la ventana vuelve a escritorio,
    // limpiamos el estado móvil.
    window.addEventListener("resize", () => {

        if (window.innerWidth > 991.98) {
            closeSidebar();
        }

    });

});