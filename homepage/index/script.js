document.addEventListener("DOMContentLoaded", function() {
    let name = prompt("What's your name?");

    const nameElement = document.getElementById("nameHeadInner");
    const textElement = document.getElementById("textHeadInner");
    const subtitleElement = document.getElementById("subtitleText");
    if (!name)
    {
        name = "Hey";
    }

    nameElement.textContent = name;

    // Sempre usar antes de dar play em uma animação que toca logo depois do browser carregar a página
    requestAnimationFrame(function() {
        nameElement.classList.add("yReset");
    })

    nameElement.addEventListener("transitionend", function() {
        textElement.classList.add("xReset");
    })

    textElement.addEventListener("transitionend", function() {
        subtitleElement.classList.add("yReset");
    })
})
