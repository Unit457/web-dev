document.addEventListener("DOMContentLoaded", () => {
    const bluebtn = document.getElementById("bluebtn");
    const purplebtn = document.getElementById("purplebtn");
    const redbtn = document.getElementById("redbtn");
    const blackbtn = document.getElementById("blackbtn");

    bluebtn.addEventListener("click", () => {
        document.body.style.backgroundColor = "rgb(0, 14, 70)";
    });

    purplebtn.addEventListener("click", () => {
        document.body.style.backgroundColor = "rgb(36, 0, 69)";
    });

    redbtn.addEventListener("click", () => {
        document.body.style.backgroundColor = "rgb(60, 0, 0)";
    });

    blackbtn.addEventListener("click", () => {
        document.body.style.backgroundColor = "#1b1b1b";
    });

    const sparkleLeft = document.getElementById("sparkleLeft");
    const websiteHeadPhrase = document.getElementById("websiteHeadPhrase");
    const sparkleRight = document.getElementById("sparkleRight");

    requestAnimationFrame(function() {
        websiteHeadPhrase.classList.add("yReset");
    })

    websiteHeadPhrase.addEventListener("transitionend", function() {
        sparkleLeft.classList.add("xReset");
        sparkleRight.classList.add("xReset");
    })
});
