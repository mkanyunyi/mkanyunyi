/* Réglages de l'écran d'accueil — modifier ici puis réinstaller (scripts/install.sh). */
window.HOME_CONFIG = {
  // Applis du dock, dans l'ordre. `match` trouve l'appli installée par son nom ;
  // `ids` sert de secours si la recherche par nom échoue (identifiants Tizen connus).
  apps: [
    { name: "Netflix",     match: /netflix/i,          ids: ["RN1MCdNq8t.Netflix", "11101200001"],
      color: "#141414", accent: "#e50914" },
    { name: "YouTube",     match: /^youtube$/i,        ids: ["9Ur5IzDKqV.TizenYouTube", "111299001912"],
      color: "#ffffff", accent: "#ff0000" },
    { name: "Prime Video", match: /prime\s*video/i,    ids: ["evKhCgZelL.AmazonIgnitionLauncher2", "org.tizen.ignition", "3201512006785"],
      color: "#0f171e", accent: "#1a98ff" }
  ],
  wallpaperSeconds: 45,     // durée d'affichage de chaque fond
  idleSeconds: 60,          // inactivité avant de masquer le dock (mode contemplation)
  captions: true            // afficher le nom du paysage en bas à gauche
};
