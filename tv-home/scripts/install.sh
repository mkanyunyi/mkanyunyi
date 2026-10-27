#!/usr/bin/env bash
# Installe l'écran d'accueil sur la TV Samsung (mode développeur Tizen).
# Usage : scripts/install.sh [IP_TV] [PROFIL_CERTIFICAT]
set -euo pipefail

TV_IP="${1:-192.168.0.170}"
PROFILE="${2:-${TIZEN_PROFILE:-tvhome}}"
APP_ID="MkTvHome01.Accueil"
SERIAL="$TV_IP:26101"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKUP="$ROOT/sauvegardes/$(date +%Y%m%d-%H%M%S)"

# Outils Tizen Studio (ajoutés au PATH s'ils sont à l'emplacement par défaut).
for d in "$HOME/tizen-studio/tools/ide/bin" "$HOME/tizen-studio/tools" "/c/tizen-studio/tools/ide/bin" "/c/tizen-studio/tools"; do
  [ -d "$d" ] && PATH="$d:$PATH"
done
command -v tizen >/dev/null || { echo "✗ 'tizen' introuvable : installe Tizen Studio (voir README)."; exit 1; }
command -v sdb   >/dev/null || { echo "✗ 'sdb' introuvable : installe Tizen Studio (voir README)."; exit 1; }

step() { printf '\n▶ %s\n' "$*"; }

step "1/6 Liste des fonds d'écran"
{
  echo "/* Généré par scripts/install.sh à partir du dossier wallpapers/ — ne pas éditer à la main. */"
  echo "window.HOME_WALLPAPERS = ["
  first=1
  for f in "$ROOT"/wallpapers/*.jpg "$ROOT"/wallpapers/*.jpeg "$ROOT"/wallpapers/*.png; do
    [ -e "$f" ] || continue
    name="$(basename "$f")"
    title="$(grep -F "$name|" "$ROOT/wallpapers/titres.txt" 2>/dev/null | head -1 | cut -d'|' -f2- || true)"
    [ -n "$title" ] || title="$(echo "${name%.*}" | sed 's/^[0-9]*-//; s/[-_]/ /g')"
    title="${title//\\/\\\\}"; title="${title//\"/\\\"}"
    [ $first -eq 1 ] || echo ","
    printf '  { file: "wallpapers/%s", title: "%s" }' "$name" "$title"
    first=0
  done
  echo; echo "];"
} > "$ROOT/js/wallpapers.js"
grep -c 'file:' "$ROOT/js/wallpapers.js" | xargs -I{} echo "  {} fond(s) d'écran"

step "2/6 Connexion à la TV ($SERIAL)"
sdb connect "$TV_IP" >/dev/null
sdb devices | grep -q "$TV_IP" || { echo "✗ TV non connectée. Mode développeur activé avec l'IP de cet ordi ? (voir README)"; exit 1; }
echo "  ✓ connectée"

step "3/6 Sauvegarde de l'état actuel → $BACKUP"
mkdir -p "$BACKUP"
sdb -s "$SERIAL" capability > "$BACKUP/tv-infos.txt" 2>&1 || true
sdb -s "$SERIAL" shell 0 vd_applist > "$BACKUP/applis-installees.txt" 2>&1 || true
cp "$ROOT/js/config.js" "$BACKUP/"
if grep -q "$APP_ID" "$BACKUP/applis-installees.txt" 2>/dev/null; then
  echo "$APP_ID déjà installée avant cette opération" > "$BACKUP/etat-accueil.txt"
else
  echo "$APP_ID absente avant cette opération" > "$BACKUP/etat-accueil.txt"
fi
echo "  ✓ $(wc -l < "$BACKUP/applis-installees.txt" | tr -d ' ') ligne(s) d'inventaire enregistrées"

step "4/6 Construction et signature (profil '$PROFILE')"
BUILD="$(mktemp -d)"
trap 'rm -rf "$BUILD"' EXIT
cp -R "$ROOT/config.xml" "$ROOT/index.html" "$ROOT/icon.png" "$ROOT/css" "$ROOT/js" "$ROOT/wallpapers" "$BUILD/"
rm -f "$BUILD/wallpapers/titres.txt"
tizen package -t wgt -s "$PROFILE" -- "$BUILD" >/dev/null
WGT="$(ls "$BUILD"/*.wgt | head -1)"
[ -f "$WGT" ] || { echo "✗ Paquet non créé : vérifie le profil de certificat Samsung '$PROFILE'."; exit 1; }
cp "$WGT" "$BACKUP/Accueil.wgt"
echo "  ✓ $(basename "$WGT") ($(du -h "$WGT" | cut -f1))"

step "5/6 Installation sur la TV"
tizen install -n "$WGT" -s "$SERIAL" | tail -3

step "6/6 Lancement et vérification"
tizen run -p "$APP_ID" -s "$SERIAL" | tail -2
if sdb -s "$SERIAL" shell 0 vd_applist 2>/dev/null | grep -q "$APP_ID"; then
  echo "  ✓ '$APP_ID' est bien installée."
else
  echo "  ? Installation non confirmée par l'inventaire : regarde l'écran de la TV."
fi
echo
echo "Terminé. Sur la TV : l'écran d'accueil doit s'afficher. Pour tout annuler : scripts/restore.sh $TV_IP"
