document.addEventListener("DOMContentLoaded", function () {

  const Cadastrar = document.getElementById("btn-cadastro");

  if (Cadastrar) {
    Cadastrar.addEventListener("click", function () {
      event.preventDefault();
      window.location.href = "../Interface-Inicial/interface.html";
    });
  }

});
