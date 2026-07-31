const questions = JSON.parse(
    document.getElementById("questions-data").textContent
);

let currentQuestion = 0;
let timeLeft = 45;
let countdown = null;

const questionNumber = document.getElementById("question-number");
const questionText = document.getElementById("question-text");
const timer = document.getElementById("timer");
const questionCard = document.getElementById("question-card");
const progressFill = document.getElementById("progress-fill");

// Load Question
function loadQuestion() {

    document.getElementById("clueBox").style.display="none";

    document.getElementById("clueText").innerHTML="";

    // Fade Out
    questionCard.animate(

[
    {
        opacity:0,
        transform:"translateY(15px)"
    },

    {
        opacity:1,
        transform:"translateY(0px)"
    }

],

{
    duration:350,

    easing:"ease-out"

});
    questionCard.style.transform = "translateY(15px)";

    setTimeout(() => {

        questionNumber.innerText =
`Question ${String(currentQuestion + 1).padStart(2, "0")} / ${String(questions.length).padStart(2, "0")}`;

        questionText.innerText =
            questions[currentQuestion].question;

        const progress =
            ((currentQuestion + 1) / questions.length) * 100;

        progressFill.style.width = progress + "%";

        // Reset Timer
        timeLeft = 45;
        timer.innerText = timeLeft;
        timer.style.color = "#2563eb";
        timer.classList.remove("timer-warning");
        timer.classList.remove("timer-danger");

        // Fade In
        questionCard.style.opacity = "1";
        questionCard.style.transform = "translateY(0)";

    }, 250);

}

// Timer
function startTimer() {

    if (countdown) {
        clearInterval(countdown);
    }

    countdown = setInterval(() => {

        timer.innerText = timeLeft;

        if(timeLeft===15){

    document.getElementById("clueText").innerHTML=
        questions[currentQuestion].clue;

    document.getElementById("clueBox").style.display="block";

}

        // Timer Color
        if (timeLeft <= 5) {

            timer.style.color = "#dc2626";
            timer.classList.add("timer-danger");
            timer.classList.remove("timer-warning");

        }
        else if (timeLeft <= 10) {

            timer.style.color = "#f59e0b";
            timer.classList.add("timer-warning");
            timer.classList.remove("timer-danger");

        }
        else {

            timer.style.color = "#2563eb";
            timer.classList.remove("timer-warning");
            timer.classList.remove("timer-danger");

        }

        if (timeLeft > 0) {

    timeLeft--;

} else {

    currentQuestion++;

    clearInterval(countdown);

    // Last Question Completed
    if (currentQuestion >= questions.length) {

        questionNumber.innerText = "";

        progressFill.style.width = "100%";

        questionCard.innerHTML = `

        <div style="text-align:center;padding:40px;animation:fadeIn .8s;">

            <div style="font-size:70px;">
                🎉 🎊 🥳
            </div>

            <img
            src="/static/images/celebration.gif"
            style="width:240px;margin:20px 0;">

            <h1 style="color:#2563eb;">
                Congratulations!
            </h1>

            <h2 style="margin-top:10px;">
                Round 2 Completed Successfully
            </h2>

            <p style="font-size:18px;color:#555;margin-top:15px;">
                Please submit your answer sheet
                to the coordinators.
            </p>

        </div>

        `;

        timer.style.display = "none";

        fetch("/riddles/complete", {
    method: "POST"
})
.then(response => response.json())
.then(data => {

    if(data.success){

        setTimeout(() => {
            window.location.href = "/dashboard";
        }, 5000);

    }

});

        return;
    }

    // Load Next Question
    loadQuestion();

startTimer();

}           // closes else

}, 1000);   // closes setInterval

}           // closes startTimer
/* =====================================
   ROUND 2 SECURITY
===================================== */


// Disable Right Click
document.addEventListener("contextmenu", function (e) {
    e.preventDefault();
});

// Disable Copy
document.addEventListener("copy", function (e) {
    e.preventDefault();
});

// Disable Cut
document.addEventListener("cut", function (e) {
    e.preventDefault();
});

// Disable Paste
document.addEventListener("paste", function (e) {
    e.preventDefault();
});

// Disable Drag
document.addEventListener("dragstart", function (e) {
    e.preventDefault();
});

// Disable Text Selection
document.addEventListener("selectstart", function (e) {
    e.preventDefault();
});

// Disable Keyboard Shortcuts
document.addEventListener("keydown", function (e) {

    // F12
    if (e.key === "F12") {
        e.preventDefault();
        return false;
    }

    // Ctrl + U
    if (e.ctrlKey && (e.key === "u" || e.key === "U")) {
        e.preventDefault();
        return false;
    }

    // Ctrl + C
    if (e.ctrlKey && (e.key === "c" || e.key === "C")) {
        e.preventDefault();
        return false;
    }

    // Ctrl + V
    if (e.ctrlKey && (e.key === "v" || e.key === "V")) {
        e.preventDefault();
        return false;
    }

    // Ctrl + X
    if (e.ctrlKey && (e.key === "x" || e.key === "X")) {
        e.preventDefault();
        return false;
    }

    // Ctrl + A
    if (e.ctrlKey && (e.key === "a" || e.key === "A")) {
        e.preventDefault();
        return false;
    }

    // Ctrl + S
    if (e.ctrlKey && (e.key === "s" || e.key === "S")) {
        e.preventDefault();
        return false;
    }

    // Ctrl + P
    if (e.ctrlKey && (e.key === "p" || e.key === "P")) {
        e.preventDefault();
        return false;
    }

    // Ctrl + Shift + I
    if (e.ctrlKey && e.shiftKey && (e.key === "I" || e.key === "i")) {
        e.preventDefault();
        return false;
    }

    // Ctrl + Shift + J
    if (e.ctrlKey && e.shiftKey && (e.key === "J" || e.key === "j")) {
        e.preventDefault();
        return false;
    }

    // Ctrl + Shift + C
    if (e.ctrlKey && e.shiftKey && (e.key === "C" || e.key === "c")) {
        e.preventDefault();
        return false;
    }

});

// Fullscreen Exit Warning
document.addEventListener("fullscreenchange", function () {

    if (!document.fullscreenElement) {

        alert("Please stay in Full Screen Mode.");

    }

});

// Start
loadQuestion();
startTimer(); 