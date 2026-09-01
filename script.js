// script.js
// Handles communication with the FastAPI backend's /predict endpoint.

const API_URL = "http://127.0.0.1:8000/predict";

const checkBtn = document.getElementById("checkBtn");
const emailText = document.getElementById("emailText");
const resultBox = document.getElementById("resultBox");
const resultIcon = document.getElementById("resultIcon");
const resultText = document.getElementById("resultText");
const confidenceText = document.getElementById("confidenceText");
const errorBox = document.getElementById("errorBox");

checkBtn.addEventListener("click", async () => {
  const text = emailText.value.trim();

  // Hide previous results/errors
  resultBox.classList.add("hidden");
  errorBox.classList.add("hidden");

  if (!text) {
    showError("الرجاء إدخال نص الرسالة قبل التحقق.");
    return;
  }

  setLoading(true);

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || `خطأ من الخادم: ${response.status}`);
    }

    const data = await response.json();
    showResult(data.prediction, data.confidence);
  } catch (err) {
    showError("تعذر الاتصال بالخادم. تأكد أن الـ backend يعمل على http://127.0.0.1:8000 (" + err.message + ")");
  } finally {
    setLoading(false);
  }
});

function setLoading(isLoading) {
  checkBtn.disabled = isLoading;
  checkBtn.textContent = isLoading ? "⏳ جاري التحقق..." : "🔍 تحقق (Check)";
}

function showResult(prediction, confidence) {
  resultBox.classList.remove("hidden", "phishing", "legitimate");
  const percent = (confidence * 100).toFixed(1);

  if (prediction === "phishing") {
    resultBox.classList.add("phishing");
    resultIcon.textContent = "⚠️";
    resultText.textContent = "رسالة تصيد احتيالي (Phishing)";
  } else {
    resultBox.classList.add("legitimate");
    resultIcon.textContent = "✅";
    resultText.textContent = "رسالة سليمة (Legitimate)";
  }

  confidenceText.textContent = `نسبة الثقة: ${percent}%`;
}

function showError(message) {
  errorBox.textContent = message;
  errorBox.classList.remove("hidden");
}
