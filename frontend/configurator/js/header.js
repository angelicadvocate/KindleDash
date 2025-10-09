export function initHeader() {
  const settingsToggle = document.getElementById("settingsToggle");
  const globalSettings = document.getElementById("globalSettings");

  settingsToggle.onclick = () => {
    globalSettings.style.display =
      globalSettings.style.display === "none" ? "block" : "none";
  };

  const shareBtn = document.getElementById("shareBtn");
  const shareMenu = document.querySelector(".share-dropdown .share-menu");

  shareBtn.onclick = () => {
    shareMenu.style.display = shareMenu.style.display === "block" ? "none" : "block";
  };

  window.addEventListener("click", function (e) {
    if (!shareBtn.contains(e.target) && !shareMenu.contains(e.target)) {
      shareMenu.style.display = "none";
    }
  });
}
