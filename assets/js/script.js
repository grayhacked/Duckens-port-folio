const button = document.getElementById("monBouton");
const titre = document.querySelector("h1");

if (button && titre) {
    button.addEventListener("click", function() {
        titre.textContent = "Merci pour votre visite !";
    });
}