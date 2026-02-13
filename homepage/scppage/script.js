document.addEventListener("DOMContentLoaded", () => {
    const play = document.getElementById("play");
    const pause = document.getElementById("pause");
    const scp = document.getElementById("scp");

    play.addEventListener("ended", () => {
        scp.play();
    });

    scp.addEventListener("pause", () => {
        pause.play();
    });
});
