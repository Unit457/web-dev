document.addEventListener("DOMContentLoaded", () => {
    const rightanswers = document.querySelectorAll(".right");

    rightanswers.forEach(button => {
        button.addEventListener("click", () => {
            if (button.style.backgroundColor == "green")
            {
                button.style.backgroundColor = "#f0f0f0";
            }
            else {
                button.style.backgroundColor = "green";
            }
        })
    })

    const wronganswers = document.querySelectorAll(".wrong");

    wronganswers.forEach(button => {
        button.addEventListener("click", () => {
            if (button.style.backgroundColor == "red")
            {
                button.style.backgroundColor = "#f0f0f0";
            }
            else {
                button.style.backgroundColor = "red";
            }
        })
    })
})
