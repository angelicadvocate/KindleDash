  const settingsToggle = document.getElementById("settingsToggle");
  const globalSettings = document.getElementById("globalSettings");
  const slidesContainer = document.getElementById("slidesContainer");
  const saveConfig = document.getElementById("saveConfig");
  const exportConfig = document.getElementById("exportConfig");

  settingsToggle.onclick = () => {
    globalSettings.style.display =
      globalSettings.style.display === "none" ? "block" : "none";
  };

  const shareBtn = document.getElementById("shareBtn");
  const shareMenu = document.querySelector(".share-dropdown .share-menu");

shareBtn.onclick = () => {
  shareMenu.style.display = shareMenu.style.display === "block" ? "none" : "block";
};

const posButtons = document.querySelectorAll('.pos-btn');

posButtons.forEach(btn => {
  btn.addEventListener('click', () => {
    // Remove active from all buttons
    posButtons.forEach(b => b.classList.remove('active'));
    // Add active to clicked button
    btn.classList.add('active');

    // Optional: store value in variable or input
    const selectedPosition = btn.dataset.pos;
    console.log('Selected Position:', selectedPosition);
    // You can also update a hidden input if your script expects a value
    // document.getElementById('overlayPosition').value = selectedPosition;
  });
});


// Optional: close dropdown if clicking outside
window.addEventListener("click", function(e) {
  if (!shareBtn.contains(e.target) && !shareMenu.contains(e.target)) {
    shareMenu.style.display = "none";
  }
});

  function createSlide(index) {
    const div = document.createElement("div");
    div.className = "slide";
    div.innerHTML = `
      <h3>Slide ${index + 1}</h3>
      <label>
        URL
        <input type="text" placeholder="https://example.com" class="slideUrl" />
      </label>
      <div class="toggle">
        <label>Invert <input type="checkbox" class="slideInvert" /></label>
        <span class="tooltip">Invert colors for better e-ink visibility</span>
      </div>
      <label>
        Scrape Interval (minutes)
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

  function gatherConfig() {
    const slides = Array.from(document.querySelectorAll(".slide")).map(slide => ({
      url: slide.querySelector(".slideUrl").value,
      invert: slide.querySelector(".slideInvert").checked,
      interval: parseInt(slide.querySelector(".slideInterval").value)
    }));

    return {
      global: {
        invert: document.getElementById("globalInvert").checked,
        defaultInterval: parseInt(document.getElementById("defaultInterval").value),
        maxRetries: parseInt(document.getElementById("maxRetries").value),
        cacheDuration: parseInt(document.getElementById("cacheDuration").value)
      },
      overlay: {
        showClock: document.getElementById("showClock").checked,
        showDate: document.getElementById("showDate").checked,
        position: document.getElementById("overlayPosition").value,
        align: document.getElementById("overlayAlign").value,
        fontFamily: document.getElementById("fontFamily").value,
        fontSize: document.getElementById("fontSize").value
      },
      slides
    };
  }

  saveConfig.onclick = () => {
    const config = gatherConfig();
    console.log("Saved Config:", config);
    alert("Configuration saved to memory!");
  };

  exportConfig.onclick = () => {
    const config = gatherConfig();
    const blob = new Blob([JSON.stringify(config, null, 2)], { type: "application/json" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "kindledash_config.json";
    link.click();
  };

  document.getElementById("resolution").addEventListener("change", function () {
    const customInputs = document.getElementById("customResolutionInputs");
    customInputs.style.display = this.value === "custom" ? "flex" : "none";
  });

  document.querySelectorAll('input[name="numSlides"]').forEach(radio => {
    radio.addEventListener('change', e => {
      updateSlides(parseInt(e.target.value));
    });
  });

  updateSlides(1);