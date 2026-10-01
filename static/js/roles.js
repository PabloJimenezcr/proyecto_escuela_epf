document.addEventListener("DOMContentLoaded", () => {

    // ========================================================
    // BUSQUEDA DE ROLES
    // ========================================================

    const searchInput =
        document.getElementById("roleSearch");

    const roleCards =
        document.querySelectorAll(".role-card");

    const emptySearch =
        document.getElementById("emptySearch");


    if (searchInput) {

        searchInput.addEventListener("input", () => {

            const searchValue =
                searchInput.value
                    .toLowerCase()
                    .trim();

            let visibleCards = 0;


            roleCards.forEach(card => {

                const roleName =
                    card.dataset.roleName || "";


                const visible =
                    roleName.includes(searchValue);


                card.style.display =
                    visible ? "" : "none";


                if (visible) {
                    visibleCards++;
                }

            });


            if (emptySearch) {

                emptySearch.style.display =
                    visibleCards === 0
                        ? "block"
                        : "none";

            }

        });

    }


    // ========================================================
    // CONTADOR DE PERMISOS
    // ========================================================

    const permissionCheckboxes =
        document.querySelectorAll(
            "[data-permission-checkbox]"
        );


    permissionCheckboxes.forEach(checkbox => {

        checkbox.addEventListener(
            "change",
            () => {

                const modal =
                    checkbox.closest(".permission-modal");


                if (!modal) {
                    return;
                }


                const selected =
                    modal.querySelectorAll(
                        "[data-permission-checkbox]:checked"
                    ).length;


                const counter =
                    modal.querySelector(
                        ".selected-permissions"
                    );


                if (counter) {

                    counter.textContent =
                        selected;

                }

            }
        );

    });


    // ========================================================
    // LIMPIAR FORMULARIO CREAR
    // ========================================================

    const createModal =
        document.getElementById("modalCrearRol");


    if (createModal) {

        createModal.addEventListener(
            "hidden.bs.modal",
            () => {

                const form =
                    document.getElementById(
                        "createRoleForm"
                    );


                if (form) {
                    form.reset();
                }

            }
        );

    }


    // ========================================================
    // VALIDACION DEL BOOTSTRAP MODAL
    // ========================================================

    // Nos permite detectar claramente si Bootstrap
    // está disponible en la página.

    if (typeof bootstrap === "undefined") {

        console.error(
            "EPF: Bootstrap JavaScript no está cargado."
        );

    } else {

        console.log(
            "EPF: Bootstrap Modal disponible correctamente."
        );

    }

});