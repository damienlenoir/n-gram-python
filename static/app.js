const EXAMPLES = [
  {
    code: "fr",
    label: "French",
    text: "Le petit chat boit du lait près de la fenêtre pendant que la pluie tombe sur la rue.",
  },
  {
    code: "en",
    label: "English",
    text: "The little cat drinks milk by the window while the rain falls on the quiet street.",
  },
  {
    code: "es",
    label: "Spanish",
    text: "El gato pequeño bebe leche junto a la ventana mientras la lluvia cae sobre la calle.",
  },
  {
    code: "de",
    label: "German",
    text: "Die kleine Katze trinkt Milch am Fenster, während der Regen auf die stille Straße fällt.",
  },
  {
    code: "it",
    label: "Italian",
    text: "Il gattino beve il latte vicino alla finestra mentre la pioggia cade sulla strada.",
  },
  {
    code: "pt",
    label: "Portuguese",
    text: "Não consigo encontrar a informação sobre a transação. A solução está na documentação da aplicação.",
  },
];

const HINTS_N = {
  1: "Unigrams: simple letter frequencies (é, ñ, ß already help).",
  2: "Bigrams: letter pairs (th, es, qu, sch…).",
  3: "Trigrams: sequences of 3 letters, often the best trade-off.",
  4: "4-grams: more precise, but fragile on short text.",
  5: "5-grams: even more specific, needs longer text.",
};

const textEl = document.getElementById("text");
const nEl = document.getElementById("n");
const nValueEl = document.getElementById("n-value");
const nHintEl = document.getElementById("n-hint");
const detectBtn = document.getElementById("detect");
const samplesEl = document.getElementById("samples");
const resultEl = document.getElementById("result");
const winnerEl = document.getElementById("winner");
const scoresEl = document.getElementById("scores");
const ngramsEl = document.getElementById("ngrams");
const errorEl = document.getElementById("error");

function showError(message) {
  errorEl.hidden = !message;
  errorEl.textContent = message || "";
}

function updateN() {
  const n = Number(nEl.value);
  nValueEl.textContent = String(n);
  nHintEl.textContent = HINTS_N[n];
}

function visibleGram(gram) {
  return gram.replaceAll(" ", "·");
}

function showResult(data) {
  resultEl.hidden = false;
  const top = data.scores[0];
  const percentage = Math.round(top.probability * 100);
  winnerEl.textContent = `${data.language_name}  ·  relative score ${percentage}%  ·  n=${data.n}`;

  scoresEl.innerHTML = "";
  const maxSim = Math.max(...data.scores.map((s) => s.similarity), 0.0001);
  for (const score of data.scores) {
    const row = document.createElement("div");
    row.className = "score";
    row.innerHTML = `
      <span>${score.name}</span>
      <div class="bar"><span style="width: ${(score.similarity / maxSim) * 100}%"></span></div>
      <span>${score.similarity.toFixed(3)}</span>
    `;
    scoresEl.appendChild(row);
  }

  ngramsEl.innerHTML = "";
  for (const item of data.top_ngrams) {
    const li = document.createElement("li");
    li.textContent = `${visibleGram(item.gram)}  ×${item.count}`;
    ngramsEl.appendChild(li);
  }
}

async function detect() {
  showError("");
  const text = textEl.value.trim();
  if (!text) {
    showError("Enter some text first.");
    return;
  }

  detectBtn.disabled = true;
  try {
    const response = await fetch("/api/detect", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, n: Number(nEl.value) }),
    });
    const data = await response.json();
    if (!response.ok) {
      const detail = data.detail;
      const message =
        typeof detail === "string"
          ? detail
          : "The request could not be processed. Check the text.";
      throw new Error(message);
    }
    showResult(data);
  } catch (error) {
    resultEl.hidden = true;
    showError(error.message);
  } finally {
    detectBtn.disabled = false;
  }
}

for (const example of EXAMPLES) {
  const button = document.createElement("button");
  button.type = "button";
  button.textContent = example.label;
  button.addEventListener("click", () => {
    textEl.value = example.text;
    showError("");
  });
  samplesEl.appendChild(button);
}

nEl.addEventListener("input", updateN);
detectBtn.addEventListener("click", detect);
updateN();
