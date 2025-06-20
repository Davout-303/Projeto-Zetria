document.addEventListener("DOMContentLoaded", function () {
  const grafosBtn = document.getElementById("grafos-btn");
  const decksBtn = document.getElementById("btn-decks");
  const caneta = document.getElementById("btn-caneta");
  const calendarioBtn = document.getElementById("calendario-btn");


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

  if (decksBtn) {
    decksBtn.addEventListener("click", function () {
      window.location.href = "../Interface-Flahscard/interface.flashcard1.html";
    });
  }

   if (calendarioBtn) {
    calendarioBtn.addEventListener("click", function () {
      window.location.href = "../Calendario/calendario.html";
    });
  };


 
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
