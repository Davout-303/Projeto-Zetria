document.addEventListener("DOMContentLoaded", function () {

  const Login = document.getElementById("btn-login");

  if (Login) {
    Login.addEventListener("click", function () {
      event.preventDefault();
      window.location.href = "../Interface-Inicial/interface.html";
    });
  }

});