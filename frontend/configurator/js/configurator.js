import { initHeader } from './header.js';
import { initGlobalSettings } from './global_settings.js';
import { initMainBody } from './main_body.js';

async function initConfigurator() {
  // Load partials
  document.getElementById('headerContainer').innerHTML = await fetch('header.html').then(r => r.text());
  document.getElementById('globalSettingsContainer').innerHTML = await fetch('global_settings.html').then(r => r.text());
  document.getElementById('mainBodyContainer').innerHTML = await fetch('main_body.html').then(r => r.text());

  // Initialize modules
  initHeader();
  initGlobalSettings();

  const slidesContainer = document.getElementById("slidesContainer");
  const { updateSlides } = initMainBody(slidesContainer);
}

initConfigurator();
