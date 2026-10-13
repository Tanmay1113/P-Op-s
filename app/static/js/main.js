"use strict";

// JavaScript is limited to interface events. Authentication and permissions live in Flask.
document.addEventListener("click", (event) => {
  const toggle = event.target.closest("[data-sidebar-toggle]");
  if (toggle) {
    document.body.classList.toggle("sidebar-open");
  }
  const dismiss = event.target.closest("[data-dismiss]");
  if (dismiss) {
    dismiss.closest(".flash")?.remove();
  }
  const passwordToggle = event.target.closest("[data-password-toggle]");
  if (passwordToggle) {
    const input = document.getElementById(passwordToggle.dataset.passwordToggle);
    if (input) {
      const visible = input.type === "password";
      input.type = visible ? "text" : "password";
      passwordToggle.textContent = visible ? "Hide" : "Show";
    }
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") document.body.classList.remove("sidebar-open");
});
