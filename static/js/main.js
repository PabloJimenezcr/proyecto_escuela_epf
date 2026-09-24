document.addEventListener("DOMContentLoaded", () => {
  const loader = document.querySelector(".loader");

  if (!loader) return;

  setTimeout(() => {
    loader.classList.add("hidden");

    setTimeout(() => {
      loader.remove();
    }, 800);
  }, 1200);
});
