document.addEventListener("DOMContentLoaded", function () {

  const Login = document.getElementById("btn-login");

  if (Login) {
    Login.addEventListener("click", function () {
      event.preventDefault();
      window.localizacao.href = "../Interface-Inicial/interface.html";
    });
  }

});