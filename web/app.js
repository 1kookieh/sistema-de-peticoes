import { initUI } from "./ui.js";

async function registerServiceWorker() {
  if (!("serviceWorker" in navigator)) return;
  try {
    await navigator.serviceWorker.register("/static/sw.js", { scope: "/" });
  } catch (error) {
    console.warn("Service worker não registrado.", error);
  }
}

await initUI();
await registerServiceWorker();
