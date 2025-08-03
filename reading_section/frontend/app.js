const loginMessage = document.getElementById('login-message');
const authSection = document.getElementById('auth-section');
const readingSection = document.getElementById('reading-section');
const questionsArea = document.getElementById('questions-area');
const submitBtn = document.getElementById('submit-btn');
const logoutBtn = document.getElementById('logout-btn');
const readingContent = document.getElementById('reading-content');

let accessToken = localStorage.getItem("access_token") || null;

// Sayfa açıldığında token var mı kontrol et ve onay sor
if (accessToken) {
  const confirmed = confirm("Token bulundu. Reading bölümüne geçmek istiyor musunuz?");
  if (confirmed) {
    authSection.style.display = 'none';
    readingSection.style.display = 'block';
    loadReadingSection();
  } else {
    loginMessage.textContent = "Reading bölümüne geçmek için onay verin.";
  }
}

// Login işlemi
document.getElementById("loginForm").addEventListener("submit", async function(event) {
  event.preventDefault();

  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value;

  if (!username || !password) {
    loginMessage.textContent = "Kullanıcı adı ve şifre gerekli.";
    return;
  }

  try {
    const response = await fetch("http://127.0.0.1:8000/auth/token", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({ username, password }),
    });

    if (!response.ok) {
      loginMessage.textContent = "Kullanıcı adı veya şifre yanlış.";
      return;
    }

    const data = await response.json();
    accessToken = data.access_token;
    localStorage.setItem("access_token", accessToken);
    loginMessage.textContent = "Giriş başarılı!";

    const confirmed = confirm("Reading bölümüne geçmek için onay verin.");
    if (confirmed) {
      authSection.style.display = 'none';
      readingSection.style.display = 'block';
      await loadReadingSection();
    } else {
      loginMessage.textContent = "Reading bölümüne geçmek için onay verin.";
    }

  } catch (error) {
    console.error("Giriş sırasında hata:", error);
    loginMessage.textContent = "Giriş sırasında bir hata oluştu.";
  }
});

async function loadReadingSection() {
  if (!accessToken) {
    alert("Lütfen önce giriş yapın.");
    return;
  }

  try {
    const res = await fetch("http://127.0.0.1:8000/reading_section", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${accessToken}`,
      },
      body: JSON.stringify({ level: "intermediate" }),
    });

    if (!res.ok) {
      alert("Okuma bölümü alınamadı.");
      return;
    }

    const data = await res.json();

    // Metni göster
    readingContent.textContent = data.reading_passage.content;

    // Soruları göster (multiple choice)
    questionsArea.innerHTML = ""; // Önce temizle
    data.questions.forEach((q, idx) => {
      const div = document.createElement("div");
      div.style.marginBottom = "15px";
      div.innerHTML = `
        <strong>Soru ${idx + 1}:</strong> ${q.question_text}<br>
        <label><input type="radio" name="q${q.id}" value="A"> A) ${q.choices.A}</label><br>
        <label><input type="radio" name="q${q.id}" value="B"> B) ${q.choices.B}</label><br>
        <label><input type="radio" name="q${q.id}" value="C"> C) ${q.choices.C}</label><br>
        <label><input type="radio" name="q${q.id}" value="D"> D) ${q.choices.D}</label>
      `;
      questionsArea.appendChild(div);
    });

    submitBtn.style.display = "inline-block";

  } catch (error) {
    console.error("Okuma bölümü yükleme hatası:", error);
    alert("Bir hata oluştu.");
  }
}

// Cevapları toplama ve geçici bildirim
submitBtn.onclick = () => {
  const answers = {};
  const inputs = questionsArea.querySelectorAll("input[type='radio']:checked");
  inputs.forEach(input => {
    answers[input.name] = input.value;
  });

  if (Object.keys(answers).length !== questionsArea.querySelectorAll("div").length) {
    alert("Tüm sorulara cevap vermelisiniz.");
    return;
  }

  console.log("Kullanıcı cevapları:", answers);
  alert("Cevaplarınız alındı. Puanlama özelliği yakında eklenecek.");
};

// Çıkış işlemi
logoutBtn.onclick = () => {
  accessToken = null;
  localStorage.removeItem("access_token");
  authSection.style.display = 'block';
  readingSection.style.display = 'none';
  readingContent.textContent = "";
  questionsArea.innerHTML = "";
  submitBtn.style.display = "none";
  loginMessage.textContent = "";
};

console.log("Frontend veritabanı destekli IELTS Reading app.js yüklendi ve çalışıyor.");