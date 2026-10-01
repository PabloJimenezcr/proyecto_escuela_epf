document.addEventListener("DOMContentLoaded", () => {

    // ========================================================
    // BUSQUEDA Y FILTROS
    // ========================================================

    const searchInput =
        document.getElementById("groupSearch");

    const levelFilter =
        document.getElementById("groupLevelFilter");

    const yearFilter =
        document.getElementById("groupYearFilter");

    const groupCards =
        document.querySelectorAll(".group-card");

    const emptyState =
        document.getElementById("groupsEmpty");

    const resultsText =
        document.getElementById("groupResultsText");


    const filterGroups = () => {

        if (!groupCards.length) {
            return;
        }


        const search =
            searchInput
                ? searchInput.value
                    .toLowerCase()
                    .trim()
                : "";


        const level =
            levelFilter
                ? levelFilter.value
                : "";


        const year =
            yearFilter
                ? yearFilter.value
                : "";


        let visible =
            0;


        groupCards.forEach(card => {

            const name =
                card.dataset.groupName || "";

            const cardLevel =
                card.dataset.groupLevel || "";

            const section =
                card.dataset.groupSection || "";

            const cardYear =
                card.dataset.groupYear || "";


            const matchesSearch =
                !search ||
                name.includes(search) ||
                cardLevel.toLowerCase().includes(search) ||
                section.toLowerCase().includes(search);


            const matchesLevel =
                !level ||
                cardLevel === level;


            const matchesYear =
                !year ||
                cardYear === year;


            const shouldShow =
                matchesSearch &&
                matchesLevel &&
                matchesYear;


            card.style.display =
                shouldShow
                    ? ""
                    : "flex";


            if (shouldShow) {
                visible++;
            }

        });


        if (emptyState) {

            emptyState.style.display =
                visible === 0
                    ? "flex"
                    : "none";

        }


        if (resultsText) {

            resultsText.innerHTML =
                `Mostrando <strong>${visible}</strong> grupos`;

        }

    };


    if (searchInput) {

        searchInput.addEventListener(
            "input",
            filterGroups
        );

    }


    if (levelFilter) {

        levelFilter.addEventListener(
            "change",
            filterGroups
        );

    }


    if (yearFilter) {

        yearFilter.addEventListener(
            "change",
            filterGroups
        );

    }


    // ========================================================
    // FORMULARIO
    // ========================================================

    const groupForm =
        document.getElementById("groupForm");

    const levelSelect =
        document.getElementById("nivel");

    const yearInput =
        document.getElementById("anio_lectivo");

    const previewLevel =
        document.getElementById("previewLevel");

    const previewName =
        document.getElementById("previewName");

    const previewYear =
        document.getElementById("previewYear");


    const updatePreview = () => {

        if (!previewLevel || !previewName) {
            return;
        }


        const selectedOption =
            levelSelect
                ? levelSelect.options[levelSelect.selectedIndex]
                : null;


        const level =
            levelSelect
                ? levelSelect.value
                : "";


        const section =
            document.querySelector(
                'input[name="seccion"]:checked'
            );


        const sectionValue =
            section
                ? section.value
                : "A";


        if (level) {

            previewLevel.textContent =
                `${level} grado`;

        } else {

            previewLevel.textContent =
                "Selecciona el nivel";

        }


        const numberMap = {
            Primero: "1°",
            Segundo: "2°",
            Tercero: "3°",
            Cuarto: "4°",
            Quinto: "5°",
            Sexto: "6°"
        };


        const number =
            numberMap[level] || "—";


        previewName.textContent =
            `${number} ${sectionValue}`;


        if (previewYear && yearInput) {

            previewYear.textContent =
                yearInput.value || "2026";

        }

    };


    if (levelSelect) {

        levelSelect.addEventListener(
            "change",
            updatePreview
        );

    }


    if (yearInput) {

        yearInput.addEventListener(
            "input",
            updatePreview
        );

    }


    document
        .querySelectorAll(
            'input[name="seccion"]'
        )
        .forEach(section => {

            section.addEventListener(
                "change",
                updatePreview
            );

        });


    updatePreview();


    // ========================================================
    // PREVENIR DOBLE ENVIO
    // ========================================================

    if (groupForm) {

        groupForm.addEventListener(
            "submit",
            () => {

                const submitButton =
                    groupForm.querySelector(
                        'button[type="submit"]'
                    );


                if (!submitButton) {
                    return;
                }


                submitButton.disabled =
                    true;


                submitButton.innerHTML =
                    `
                    <i class="ri-loader-4-line ri-spin"></i>
                    Creando grupo...
                    `;

            }
        );

    }

});