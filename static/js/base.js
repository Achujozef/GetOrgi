  document.addEventListener("DOMContentLoaded", function () {

  const toggler = document.querySelector(".navbar-toggler");

  const icon = toggler.querySelector("i");

  const collapse = document.getElementById("navbarNav");

  // Sync icon with Bootstrap collapse

  collapse.addEventListener("show.bs.collapse", () => {

   icon.classList.remove("fa-bars");

   icon.classList.add("fa-times");

  });

  collapse.addEventListener("hide.bs.collapse", () => {

   icon.classList.remove("fa-times");

   icon.classList.add("fa-bars");

  });

  });