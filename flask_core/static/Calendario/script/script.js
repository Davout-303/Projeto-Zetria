document.addEventListener("DOMContentLoaded", function () {
  
  const grafosBtn = document.getElementById("grafos-btn");
  const decksBtn = document.getElementById("btn-decks");
  const caneta = document.getElementById("btn-caneta");


  if (caneta) {
    caneta.addEventListener("click", function () {
      window.localizacao.href = "../Criacao-nota/index.html";
    });
  }


  if (grafosBtn) {
    grafosBtn.addEventListener("click", function () {
      window.localizacao.href = "../Anotacoes-grafos/index.html";
    });
  }

  if (decksBtn) {
    decksBtn.addEventListener("click", function () {
      window.localizacao.href = "../Interface-Flahscard/interface.flashcard1.html";
    });
  }

  
  const menuToggle = document.getElementById("menuAlternar");
  const sidebar = document.getElementById("barra-lateral");

  menuToggle.addEventListener("click", () => {
    sidebar.classList.toggle("ativo");

    const icon = menuToggle.querySelector("i");
    if (sidebar.classList.contains("ativo")) {
      icon.classList.remove("fa-bars");
      icon.classList.add("fa-times");
    } else {
      icon.classList.remove("fa-times");
      icon.classList.add("fa-bars");
    }
  });

  
  const sidebarItems = document.querySelectorAll(".barraLateral-item");
  sidebarItems.forEach((item) => {
    item.addEventListener("click", () => {
      if (window.innerWidth <= 768) {
        sidebar.classList.remove("ativo");
        const icon = menuToggle.querySelector("i");
        icon.classList.remove("fa-times");
        icon.classList.add("fa-bars");
      }
    });
  });
});
