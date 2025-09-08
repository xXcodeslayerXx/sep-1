let startTime = null;
let elapsedTime = 0;
let timerInterval = null;
let isRunning = false;
let isPaused = false;

const timer = document.getElementById("timer");
const startBtn = document.getElementById("startBtn");
const pauseBtn = document.getElementById("pauseBtn");
const stopBtn = document.getElementById("stopBtn");
const resetBtn = document.getElementById("resetBtn");
const saveSessionBtn = document.getElementById("saveSessionBtn");
const startTimeDisplay = document.getElementById("startTime");
const endTimeDisplay = document.getElementById("endTime");
const totalTimeDisplay = document.getElementById("totalTime");

function formatTime(ms) {
  const hours = Math.floor(ms / 3600000);
  const minutes = Math.floor((ms % 3600000) / 60000);
  const seconds = Math.floor((ms % 60000) / 1000);
  return `${hours.toString().padStart(2, "0")}:${minutes
    .toString()
    .padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
}

function updateTimer() {
  const timer = document.getElementById("timer");
  const currentTime = Date.now();
  elapsedTime = currentTime - startTime;
  if (timer) timer.textContent = formatTime(elapsedTime);
}

function startTimer() {
  const startBtn = document.getElementById("startBtn");
  const pauseBtn = document.getElementById("pauseBtn");
  const stopBtn = document.getElementById("stopBtn");
  const resetBtn = document.getElementById("resetBtn");
  const startTimeDisplay = document.getElementById("startTime");
  if (!isRunning) {
    startTime = Date.now() - elapsedTime;
    timerInterval = setInterval(updateTimer, 1000);
    isRunning = true;
    isPaused = false;

    if (startBtn) startBtn.disabled = true;
    if (pauseBtn) pauseBtn.disabled = false;
    if (stopBtn) stopBtn.disabled = false;
    if (resetBtn) resetBtn.disabled = true;

    const now = new Date();
    if (startTimeDisplay)
      startTimeDisplay.textContent = now.toLocaleTimeString();
  }
}

function pauseTimer() {
  const pauseBtn = document.getElementById("pauseBtn");
  if (isRunning && !isPaused) {
    clearInterval(timerInterval);
    isPaused = true;
    if (pauseBtn) pauseBtn.textContent = "Resume";
  } else if (isPaused) {
    startTime = Date.now() - elapsedTime;
    timerInterval = setInterval(updateTimer, 1000);
    isPaused = false;
    if (pauseBtn) pauseBtn.textContent = "Pause";
  }
}

function stopTimer() {
  const startBtn = document.getElementById("startBtn");
  const pauseBtn = document.getElementById("pauseBtn");
  const stopBtn = document.getElementById("stopBtn");
  const resetBtn = document.getElementById("resetBtn");
  const saveSessionBtn = document.getElementById("saveSessionBtn");
  const endTimeDisplay = document.getElementById("endTime");
  const totalTimeDisplay = document.getElementById("totalTime");
  if (isRunning) {
    clearInterval(timerInterval);
    isRunning = false;
    isPaused = false;

    if (startBtn) startBtn.disabled = false;
    if (pauseBtn) pauseBtn.disabled = true;
    if (stopBtn) stopBtn.disabled = true;
    if (resetBtn) resetBtn.disabled = false;
    if (saveSessionBtn) saveSessionBtn.disabled = false;

    const now = new Date();
    if (endTimeDisplay) endTimeDisplay.textContent = now.toLocaleTimeString();
    if (totalTimeDisplay)
      totalTimeDisplay.textContent = formatTime(elapsedTime);

    if (pauseBtn) pauseBtn.textContent = "Pause";
  }
}

function resetTimer() {
  const timer = document.getElementById("timer");
  const startBtn = document.getElementById("startBtn");
  const pauseBtn = document.getElementById("pauseBtn");
  const stopBtn = document.getElementById("stopBtn");
  const resetBtn = document.getElementById("resetBtn");
  const saveSessionBtn = document.getElementById("saveSessionBtn");
  const startTimeDisplay = document.getElementById("startTime");
  const endTimeDisplay = document.getElementById("endTime");
  const totalTimeDisplay = document.getElementById("totalTime");
  clearInterval(timerInterval);
  elapsedTime = 0;
  isRunning = false;
  isPaused = false;

  if (timer) timer.textContent = "00:00:00";
  if (startTimeDisplay) startTimeDisplay.textContent = "--:--:--";
  if (endTimeDisplay) endTimeDisplay.textContent = "--:--:--";
  if (totalTimeDisplay) totalTimeDisplay.textContent = "00:00:00";

  if (startBtn) startBtn.disabled = false;
  if (pauseBtn) pauseBtn.disabled = true;
  if (stopBtn) stopBtn.disabled = true;
  if (resetBtn) resetBtn.disabled = false;
  if (saveSessionBtn) saveSessionBtn.disabled = true;

  if (pauseBtn) pauseBtn.textContent = "Pause";
}

function saveSession() {
  const saveSessionBtn = document.getElementById("saveSessionBtn");
  const startTimeDisplay = document.getElementById("startTime");
  const endTimeDisplay = document.getElementById("endTime");

  if (
    !startTimeDisplay ||
    !endTimeDisplay ||
    startTimeDisplay.textContent === "--:--:--"
  ) {
    alert("Please complete a study session before saving.");
    return;
  }

  // Get the subject from the page (you might need to pass this from the template)
  const subjectElement = document.querySelector(".badge.bg-primary");
  const subject = subjectElement ? subjectElement.textContent : "General";

  const studyData = {
    subject: subject,
    timeSpentSeconds: Math.floor(elapsedTime / 1000), // Convert milliseconds to seconds
    startTime: startTimeDisplay.textContent,
    endTime: endTimeDisplay.textContent,
  };

  // Send data to server
  fetch("/save-study-session", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(studyData),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "success") {
        alert("Study session saved successfully!");
        if (saveSessionBtn) saveSessionBtn.disabled = true;
      } else {
        alert("Error saving session: " + data.message);
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("Error saving session. Please try again.");
    });
}

document.addEventListener("DOMContentLoaded", function () {
  const startBtn = document.getElementById("startBtn");
  const pauseBtn = document.getElementById("pauseBtn");
  const stopBtn = document.getElementById("stopBtn");
  const resetBtn = document.getElementById("resetBtn");
  const saveSessionBtn = document.getElementById("saveSessionBtn");
  if (startBtn) startBtn.addEventListener("click", startTimer);
  if (pauseBtn) pauseBtn.addEventListener("click", pauseTimer);
  if (stopBtn) stopBtn.addEventListener("click", stopTimer);
  if (resetBtn) resetBtn.addEventListener("click", resetTimer);
  if (saveSessionBtn) saveSessionBtn.addEventListener("click", saveSession);
  resetTimer();
});
