document.addEventListener("DOMContentLoaded", function () {

  const grafosBtn = document.getElementById("grafos-btn");
  const calendarioBtn = document.getElementById("calendario-btn");
  const decksBtn = document.getElementById("btn-decks");
  const caneta = document.getElementById("btn-caneta");

  if (caneta) {
    caneta.addEventListener("click", function () {
      window.location.href = "../Criacao-nota/index.html";
    });
  }

  if (grafosBtn) {
    grafosBtn.addEventListener("click", function () {
      window.location.href = "../Anotacoes-grafos/index.html";
    });
  }

  if (calendarioBtn) {
    calendarioBtn.addEventListener("click", function () {
      window.location.href = "../Calendario/calendario.html";
    });
  }

  if (decksBtn) {
    decksBtn.addEventListener("click", function () {
      window.location.href = "../Interface-Flahscard/interface.flashcard1.html";
    });
  }

  
  const menuToggle = document.getElementById("menuToggle");
  const sidebar = document.getElementById("sidebar");

  menuToggle.addEventListener("click", () => {
    sidebar.classList.toggle("active");

    const icon = menuToggle.querySelector("i");
    if (sidebar.classList.contains("active")) {
      icon.classList.remove("fa-bars");
      icon.classList.add("fa-times");
    } else {
      icon.classList.remove("fa-times");
      icon.classList.add("fa-bars");
    }
  });

  
  const sidebarItems = document.querySelectorAll(".sidebar-item");
  sidebarItems.forEach((item) => {
    item.addEventListener("click", () => {
      if (window.innerWidth <= 768) {
        sidebar.classList.remove("active");
        const icon = menuToggle.querySelector("i");
        icon.classList.remove("fa-times");
        icon.classList.add("fa-bars");
      }
    });
  });
});
