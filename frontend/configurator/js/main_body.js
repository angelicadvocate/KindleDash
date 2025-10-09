export function initMainBody(slidesContainer) {

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

  // Initialize first slide
  updateSlides(1);

  return { updateSlides };
}
