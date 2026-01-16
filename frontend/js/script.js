const API_BASE = "http://127.0.0.1:8000/api";

const ui = {
  emailSubject: document.getElementById("emailSubject"), 
  emailText: document.getElementById("emailText"),
  fileInput: document.getElementById("fileInput"),
  fileName: document.getElementById("fileName"),
  analyzeBtn: document.getElementById("analyzeBtn"),
  loading: document.getElementById("loading"),

  resultBox: document.getElementById("resultBox"),
  categoryBadge: document.getElementById("categoryBadge"),
  responseBox: document.getElementById("responseBox"),
  previewBox: document.getElementById("previewBox"),

  historyList: document.getElementById("historyList"),
  clearHistoryBtn: document.getElementById("clearHistoryBtn"),

  confidenceValue: document.getElementById("confidenceValue"),
  confidenceFill: document.getElementById("confidenceFill"),

  dropZone: document.getElementById("dropZone"),
  errorBox: document.getElementById("errorBox"),
};

function setLoading(state) {
  ui.loading.classList.toggle("hidden", !state);
  ui.analyzeBtn.disabled = state;
}

function showError(msg) {
  ui.errorBox.textContent = msg;
  ui.errorBox.classList.remove("hidden");
}

function clearError() {
  ui.errorBox.classList.add("hidden");
}

function clearResult() {
  ui.resultBox.classList.add("hidden");
  ui.previewBox.textContent = "";
  ui.responseBox.textContent = "";
  ui.confidenceFill.style.width = "0%";
  ui.confidenceValue.textContent = "";
}

function showResult(data) {
  ui.resultBox.classList.remove("hidden");

  // Categoria 
  ui.categoryBadge.textContent = data.category;
  ui.categoryBadge.className = "badge " + data.category.toLowerCase();

  // Intenção e Fonte (IA vs Regras)
  const intentElement = document.getElementById("intentText");
  if (intentElement) {
    intentElement.textContent = data.intent;
    intentElement.className = "intent-" + data.intent.toLowerCase();
  }

  const sourceElement = document.getElementById("sourceBadge");
  if (sourceElement) {
    sourceElement.textContent = data.source === "ml_model" ? "🤖 IA (Machine Learning)" : "⚙️ Regras de Negócio";
  }

  // Resposta Sugerida
  ui.responseBox.textContent = data.suggested_reply;

  // Barra de Confiança
  const percent = Math.round(data.confidence * 100);
  ui.confidenceValue.textContent = percent + "%";
  ui.confidenceFill.style.width = percent + "%";

  // Prévia do Texto do backend
  ui.previewBox.textContent = data.text 
    ? data.text.slice(0, 2000) 
    : "Processamento concluído.";
}


function saveHistory(item) {
  const history = JSON.parse(localStorage.getItem("emailHistory")) || [];
  history.unshift(item);
  localStorage.setItem("emailHistory", JSON.stringify(history.slice(0, 10)));
  renderHistory();
}

function renderHistory() {
  const history = JSON.parse(localStorage.getItem("emailHistory")) || [];
  ui.historyList.innerHTML = "";

  history.forEach((h) => {
    const li = document.createElement("li");
    li.className = "history-item";
    li.innerHTML = `
        <strong>${h.intent || h.category}</strong>
        <span style="display:block; font-size:11px; color:var(--muted)">${h.preview}...</span>
    `;
    li.style.cursor = "pointer";
    li.onclick = () => { 
        ui.emailText.value = h.fullText || ""; 
        ui.emailSubject.value = h.subject || "";
    };
    ui.historyList.appendChild(li);
  });
}

ui.clearHistoryBtn.addEventListener("click", () => {
  localStorage.removeItem("emailHistory");
  renderHistory();
});


async function classifyText(subject, text) {
  const response = await fetch(`${API_BASE}/classify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ subject, text }),
  });

  if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Erro ao classificar texto");
  }
  return response.json();
}

async function classifyFile(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE}/classify-file`, {
    method: "POST",
    body: formData,
  });

  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || "Erro ao classificar arquivo");

  return data;
}

// Seleção de arquivo via input
ui.fileInput.addEventListener("change", () => {
  ui.fileName.textContent = ui.fileInput.files.length ? ui.fileInput.files[0].name : "Nenhum arquivo selecionado";
});

// Drag & Drop handlers
ui.dropZone.addEventListener("dragover", (e) => { e.preventDefault(); ui.dropZone.classList.add("dragover"); });
ui.dropZone.addEventListener("dragleave", () => ui.dropZone.classList.remove("dragover"));
ui.dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  ui.dropZone.classList.remove("dragover");
  const file = e.dataTransfer.files[0];
  if (file) {
    ui.fileInput.files = e.dataTransfer.files;
    ui.fileName.textContent = file.name;
  }
});

ui.analyzeBtn.addEventListener("click", async () => {
  clearError();
  clearResult();

  const text = ui.emailText.value.trim();
  const subject = ui.emailSubject.value.trim();
  const file = ui.fileInput.files[0];


  if (!text && !file) {
    showError("Informe um texto ou selecione um arquivo.");
    return; 
  }

  if (file && file.size > 2 * 1024 * 1024) {
    showError("Arquivo muito grande (máx. 2MB).");
    return; 
  }

  if (!file && text.length < 5) {
    showError("O conteúdo do e-mail é muito curto para análise.");
    return; 
  }

  
  try {
    setLoading(true); 

    let result;
    if (file) {
      result = await classifyFile(file);
    } else {
      result = await classifyText(subject, text);
    }

    showResult(result);

    saveHistory({
      category: result.category,
      intent: result.intent,
      subject: subject,
      preview: (subject || text || file.name).slice(0, 40),
      fullText: text || ""
    });

    
    ui.emailText.value = "";
    ui.emailSubject.value = "";
    ui.fileInput.value = "";
    ui.fileName.textContent = "Nenhum arquivo selecionado";

  } catch (err) {
    console.error(err);
    showError(err.message || "Erro ao processar a solicitação.");
  } finally {
    // Garante o loading 
    setLoading(false);
  }
});


renderHistory();

// Botão de Copiar Resposta
document.getElementById("copyBtn").addEventListener("click", () => {
    const text = ui.responseBox.textContent;
    navigator.clipboard.writeText(text).then(() => {
        const originalText = ui.copyBtn.textContent;
        ui.copyBtn.textContent = "Copiado!";
        setTimeout(() => ui.copyBtn.textContent = originalText, 2000);
    });
});