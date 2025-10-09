/* === Element References === */
const settingsToggle = document.getElementById("settingsToggle");
const globalSettings = document.getElementById("globalSettings");
const slidesContainer = document.getElementById("slidesContainer");
const saveConfig = document.getElementById("saveConfig");
const exportConfig = document.getElementById("exportConfig");

let showTime = false;
let showDate = false;

/* === Header / Settings Toggles === */
settingsToggle.onclick = () => {
  globalSettings.style.display =
    globalSettings.style.display === "none" ? "block" : "none";
};

const shareBtn = document.getElementById("shareBtn");
const shareMenu = document.querySelector(".share-dropdown .share-menu");

shareBtn.onclick = () => {
  shareMenu.style.display = shareMenu.style.display === "block" ? "none" : "block";
};

window.addEventListener("click", function(e) {
  if (!shareBtn.contains(e.target) && !shareMenu.contains(e.target)) {
    shareMenu.style.display = "none";
  }
});

/* === Overlay Position Buttons === */
const posButtons = document.querySelectorAll('.pos-btn');

posButtons.forEach(btn => {
  btn.addEventListener('click', () => {
    posButtons.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
  });
});

/* === Toggle Buttons === */
document.querySelectorAll('.toggle-btn').forEach(button => {
  button.addEventListener('click', () => {
    button.classList.toggle('active');
    const isActive = button.classList.contains('active');
    const target = button.dataset.target;

    if (target === 'showTime') showTime = isActive;
    else if (target === 'showDate') showDate = isActive;

    updatePreview();
  });
});

/* === Slide Buttons === */
document.querySelectorAll('.slide-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.slide-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const count = parseInt(btn.dataset.slides);
    updateSlides(count);
  });
});

/* === Slides Functions === */
function createSlide(index) {
  const div = document.createElement("div");
  div.className = "slide";
  div.innerHTML = `
    <h3>Slide ${index + 1}</h3>
    <label>
      URL
      <span class="tooltip">The webpage or dashboard you want to display on this slide.</span>
      <input type="text" placeholder="https://example.com" class="slideUrl" />
    </label>
    <div class="toggle">
      <label>Invert <input type="checkbox" class="slideInvert" /></label>
      <span class="tooltip">Invert colors for better e-ink visibility</span>
    </div>
    <label>
      Scrape Interval (minutes)
      <span class="tooltip">How often this slide refreshes content from the URL.</span>
      <input type="number" value="5" min="1" class="slideInterval" />
    </label>
    <button class="testSlide">Test Slide ${index + 1}</button>
    <div class="slidePreview">
      <p>No preview yet.</p>
    </div>
  `;

  const testButton = div.querySelector(".testSlide");
  const preview = div.querySelector(".slidePreview");

  testButton.onclick = () => {
    preview.innerHTML = "<p>Fetching preview...</p>";
    setTimeout(() => {
      preview.innerHTML = `<img src="https://placehold.co/400x300?text=Slide+${index + 1}+Preview" alt="Preview" />`;
    }, 1000);
  };

  return div;
}

function updateSlides(count) {
  slidesContainer.innerHTML = "";
  for (let i = 0; i < count; i++) {
    slidesContainer.appendChild(createSlide(i));
  }
}

/* === Preview Update Hook === */
function updatePreview() {
  // Placeholder: could update overlay preview dynamically
}

/* === Gather All Config === */
function gatherConfig() {
  const slides = Array.from(document.querySelectorAll(".slide")).map(slide => ({
    url: slide.querySelector(".slideUrl").value,
    invert: slide.querySelector(".slideInvert").checked,
    interval: parseInt(slide.querySelector(".slideInterval").value)
  }));

  const positionBtn = document.querySelector('.pos-btn.active');

  return {
    global: {
      invert: document.getElementById("globalInvert")?.checked || false,
      defaultInterval: parseInt(document.getElementById("defaultInterval")?.value) || 5,
      maxRetries: parseInt(document.getElementById("maxRetries")?.value) || 3,
      cacheDuration: parseInt(document.getElementById("cacheDuration")?.value) || 30
    },
    overlay: {
      showTime,
      showDate,
      position: positionBtn ? positionBtn.dataset.pos : 'none',
      align: document.getElementById("overlayAlign")?.value || 'center',
      fontFamily: document.getElementById("fontFamily")?.value || 'sans-serif',
      fontSize: document.getElementById("fontSize")?.value || 'medium'
    },
    slides
  };
}

/* === Save / Export Buttons === */
saveConfig.onclick = () => {
  const config = gatherConfig();
  console.log("Saved Config:", config);
  alert("Configuration saved!");
  // Later: POST this config to backend
};

exportConfig.onclick = () => {
  const config = gatherConfig();
  const blob = new Blob([JSON.stringify(config, null, 2)], { type: "application/json" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "kindledash_config.json";
  link.click();
};

/* === Resolution Custom Input Toggle === */
document.getElementById("resolution")?.addEventListener("change", function () {
  const customInputs = document.getElementById("customResolutionInputs");
  customInputs.style.display = this.value === "custom" ? "flex" : "none";
});

/* === Initialize First Slide === */
updateSlides(1);
