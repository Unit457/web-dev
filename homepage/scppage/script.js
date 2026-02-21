document.addEventListener("DOMContentLoaded", () => {
    const playBtn = document.getElementById("play");
    const pauseBtn = document.getElementById("pause");
    const resetBtn = document.getElementById("reset")
    const scpAudio = document.getElementById("scp");
    const playSound = document.getElementById("playSound");
    const pauseSound = document.getElementById("pauseSound");

    playBtn.addEventListener("click", () => {
        playSound.play();
        setTimeout(() => {
            scpAudio.play();
        }, 1500);
    });

    pauseBtn.addEventListener("click", () => {
        scpAudio.pause();
        pauseSound.play();
    });

    resetBtn.addEventListener("click", () => {
        scpAudio.pause();
        scpAudio.currentTime = 0;
        pauseSound.play();
    });

    const content = document.getElementById("content");

    scpAudio.ontimeupdate = () => {
        if (scp.currentTime >= 27) {
        content.classList.add("anim");
        }
    };
});
