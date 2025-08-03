let chartInstance = null;
let timerInterval;
let timeLeft = 60 * 60;

function formatTime(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

function updateTimerDisplay() {
  const display = document.getElementById('timerDisplay');
  display.textContent = formatTime(timeLeft);
}

function startTimer() {
  clearInterval(timerInterval);
  timeLeft = 60 * 60;
  updateTimerDisplay();

  timerInterval = setInterval(() => {
    timeLeft--;
    updateTimerDisplay();
    if (timeLeft <= 0) {
      clearInterval(timerInterval);
      alert("⏰ Your time is up! Please send your essay.");
    }
  }, 1000);
}

let selectedTaskType = "";

function setTaskType(taskType) {
  selectedTaskType = taskType;
}

async function submitEssay() {
  const userId = document.getElementById("userIdInput").value.trim();

  if (userId.length !== 6 || isNaN(userId)) {
    alert("Please enter a valid 6-digit numeric User ID.");
    return;
  }

  if (!selectedTaskType) {
    alert("Please select Task 1 or Task 2 for evaluation.");
    return;
  }

  const essayText = document.getElementById("essay").value;

  try {
    const response = await fetch("http://127.0.0.1:8000/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: userId, text: essayText, task_type: selectedTaskType })
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("❌ Backend error response:", errorText);
      alert("❌ An error occurred while evaluating the essay.");
      return;
    }

    const result = await response.json();
    const evaluation = result.evaluation;

    document.getElementById("result").innerText = evaluation;

    const scores = {
      task: parseFloat(extractBandScore(evaluation, ["Task Achievement", "Task Response"])),
      coherence: parseFloat(extractBandScore(evaluation, ["Coherence and Cohesion"])),
      lexical: parseFloat(extractBandScore(evaluation, ["Lexical Resource"])),
      grammar: parseFloat(extractBandScore(evaluation, ["Grammatical Range and Accuracy"])),
      overall: parseFloat(extractBandScore(evaluation, ["Overall Band Score"]))
    };

    drawChart(scores);
    fetchHistory(userId);
  } catch (error) {
    console.error("❌ JS error in submitEssay:", error);
    alert("❌ Failed to connect to backend. Check the terminal.");
  }
}




function extractBandScore(text, possibleTitles) {
  for (const title of possibleTitles) {
    const regex = new RegExp(`\\*\\*${title} \\(Band ([0-9\\.]+)\\):?\\*\\*`, "i");
    const match = text.match(regex);
    if (match) return match[1];
  }
  return null;
}

function drawChart(scores) {
  const ctx = document.getElementById("scoreChart").getContext("2d");

  if (chartInstance) chartInstance.destroy();

  chartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Task Response", "Coherence & Cohesion", "Lexical Resource", "Grammar", "Overall"],
      datasets: [{
        label: "Band Score",
        data: [scores.task, scores.coherence, scores.lexical, scores.grammar, scores.overall],
        backgroundColor: ["#4e73df", "#1cc88a", "#36b9cc", "#f6c23e", "#e74a3b"]
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: { beginAtZero: true, max: 9 }
      }
    }
  });
}

async function correctEssay() {
  const essayText = document.getElementById("essay").value;
  const username = document.getElementById("userIdInput").value; // ID'yi al

  const response = await fetch("http://127.0.0.1:8000/correct", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      username: username,
      text: essayText,
      task_type: selectedTaskType
    })
  });

  const data = await response.json();
  document.getElementById("highlightedText").innerHTML = data.highlighted_text;
  document.getElementById("correctedText").innerText = data.corrected_text;

  const section = document.getElementById("correctedSection");
  section.style.display = "block";
  section.scrollIntoView({ behavior: "smooth" });
}


async function improveEssay() {
  const essayText = document.getElementById("essay").value;
  const username = document.getElementById("userIdInput").value;

  const response = await fetch("http://127.0.0.1:8000/improve", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      username: username,
      text: essayText,
      task_type: selectedTaskType
    })
  });

  const data = await response.json();
  document.getElementById("improvedText").innerText = data.improved_text;

  const section = document.getElementById("improvedSection");
  section.style.display = "block";
  section.scrollIntoView({ behavior: "smooth" });
}


async function analyzeEssay() {
  const essayText = document.getElementById("essay").value;
  const username = document.getElementById("userIdInput").value;

  const response = await fetch("http://127.0.0.1:8000/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      username: username,
      text: essayText,
      task_type: selectedTaskType
    })
  });

  const data = await response.json();
  document.getElementById("wordCount").innerText = data.word_count;
  document.getElementById("grammarMistakes").innerText = data.grammar_mistake_count;

  const list = document.getElementById("vocabRepetitionList");
  list.innerHTML = "";
  data.vocab_repetition.forEach(item => {
    const li = document.createElement("li");
    li.innerText = `${item.word} (${item.count} times)`;
    list.appendChild(li);
  });

  drawVocabChart(data.vocab_levels);
}


function drawVocabChart(data) {
  const ctx = document.getElementById("vocabChart").getContext("2d");

  if (window.vocabChart instanceof Chart) window.vocabChart.destroy();

  window.vocabChart = new Chart(ctx, {
    type: 'pie',
    data: {
      labels: Object.keys(data),
      datasets: [{
        label: 'Vocabulary Complexity',
        data: Object.values(data),
        backgroundColor: ['#ff6384', '#36a2eb', '#ffcd56', '#4bc0c0', '#9966ff']
      }]
    },
    options: { responsive: false }
  });
}

async function fetchHistory(username = "guest") {
  try {
    const response = await fetch(`http://127.0.0.1:8000/history/${username}`);
    const data = await response.json();
    console.log("Gelen geçmiş verisi:", data);

    if (!Array.isArray(data) || data.length === 0) return;

    drawHistoryChart(data);
    document.getElementById("historySection").style.display = "block";
  } catch (error) {
    console.error("Error fetching history:", error);
  }
}

function drawHistoryChart(historyData) {
  const ctx = document.getElementById("historyChart").getContext("2d");

  const labels = historyData.map(entry => {
    const date = new Date(entry.date);
    return date.toLocaleString("tr-TR");
  });

  const overallScores = historyData.map(entry => entry.overall);

  if (window.historyChart instanceof Chart) window.historyChart.destroy();

  window.historyChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Overall Band Score',
        data: overallScores,
        borderColor: '#e3092a',
        backgroundColor: 'rgba(149,12,37,0.2)',
        fill: true,
        tension: 0.3,
        pointRadius: 5
      }]
    },
    options: {
      responsive: false,
      scales: {
        y: { beginAtZero: true, max: 9 }
      }
    }
  });
}






window.addEventListener("load", () => fetchHistory("guest"));