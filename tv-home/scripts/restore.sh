#!/usr/bin/env bash
# Restaure la TV dans son état d'origine : désinstalle l'écran d'accueil et coupe la connexion.
# Rien d'autre n'a été modifié par install.sh. Usage : scripts/restore.sh [IP_TV]
set -euo pipefail

TV_IP="${1:-192.168.0.170}"
APP_ID="MkTvHome01.Accueil"
PKG_ID="MkTvHome01"
SERIAL="$TV_IP:26101"

for d in "$HOME/tizen-studio/tools/ide/bin" "$HOME/tizen-studio/tools" "/c/tizen-studio/tools/ide/bin" "/c/tizen-studio/tools"; do
  [ -d "$d" ] && PATH="$d:$PATH"
done
command -v sdb >/dev/null || { echo "✗ 'sdb' introuvable (Tizen Studio)."; exit 1; }

sdb connect "$TV_IP" >/dev/null
sdb devices | grep -q "$TV_IP" || { echo "✗ TV non joignable : mode développeur encore actif ?"; exit 1; }

echo "▶ Désinstallation de l'écran d'accueil"
if command -v tizen >/dev/null; then
  tizen uninstall -p "$APP_ID" -s "$SERIAL" | tail -2 || true
else
  sdb -s "$SERIAL" shell 0 vd_appuninstall "$PKG_ID" || true
fi

if sdb -s "$SERIAL" shell 0 vd_applist 2>/dev/null | grep -q "$APP_ID"; then
  echo "✗ L'appli est toujours présente : désinstalle-la depuis Applis › Paramètres › Supprimer."
  exit 1
fi
echo "  ✓ appli retirée"

sdb disconnect "$TV_IP" >/dev/null || true
echo "  ✓ connexion fermée"
cat <<'TXT'

Dernière étape (manuelle, pour revenir exactement à l'état d'origine) :
  Applis → tape 1 2 3 4 5 sur la télécommande → Mode développeur : Off → redémarre la TV
  (maintenir le bouton marche jusqu'au logo Samsung).
TXT
