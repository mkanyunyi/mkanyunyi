# Accueil — écran d'accueil minimaliste pour TV Samsung

Dock Netflix · YouTube · Prime Video, horloge, fonds nature qui défilent avec un léger zoom.
Après 60 s sans action, le dock s'efface (mode contemplation). Une touche le fait revenir.

| Touche | Action |
|---|---|
| ◀ ▶ | changer d'appli |
| OK | ouvrir l'appli |
| Retour | quitter (retour au Smart Hub) |

> Limite de Tizen : une appli tierce ne peut pas remplacer l'écran d'accueil Samsung.
> « Accueil » s'installe comme une appli. Place-la en premier dans la barre du Smart Hub
> (Applis → maintenir OK sur l'icône → Déplacer).

## Installation (une seule fois, ~20 min)

À faire depuis un ordi connecté au même Wi-Fi que la TV.

1. **Tizen Studio** : installe-le depuis developer.samsung.com/smarttv. Ensuite, dans le
   *Package Manager*, onglet *Extension SDK*, installe **TV Extensions** et **Samsung Certificate Extension**.
2. **Mode développeur sur la TV** : ouvre *Applis*, tape **1 2 3 4 5** sur la télécommande, passe
   *Developer mode* sur **On**, saisis l'**adresse IP de ton ordi**, puis redémarre la TV
   (maintiens le bouton marche jusqu'au logo).
3. **Certificat Samsung** : dans Tizen Studio, ouvre *Tools › Device Manager* et connecte
   `192.168.0.170`. Ensuite, dans *Tools › Certificate Manager*, clique sur **+** et choisis
   *Samsung* › *TV*. Nomme le profil **tvhome** et connecte-toi avec un compte Samsung.
   L'identifiant (DUID) de la TV est ajouté automatiquement.
4. **Installation** :
   ```bash
   cd tv-home
   ./scripts/install.sh 192.168.0.170 tvhome
   ```
   Le script régénère la liste des fonds, connecte la TV et **sauvegarde l'inventaire de ses applis**
   dans `sauvegardes/<date>/`. Il construit et signe ensuite le paquet, l'installe, le lance et vérifie.

Sous Windows, lance les scripts depuis **Git Bash**.

## Personnaliser

- **Applis du dock** : édite `js/config.js`. L'appli est trouvée par son nom sur la TV et son icône
  officielle est reprise automatiquement. Le logo texte ne sert que de secours.
- **Fonds d'écran** : dépose tes photos (JPG, 1920×1080) dans `wallpapers/`, ajoute éventuellement
  un titre dans `wallpapers/titres.txt`, puis relance `install.sh`.
  `scripts/gen_wallpapers.py` régénère les 6 paysages fournis.
- Durées (rotation des fonds, mise en veille du dock) : `js/config.js`.

## Tout restaurer

```bash
./scripts/restore.sh 192.168.0.170
```

Le script désinstalle l'appli et ferme la connexion. Il rappelle ensuite l'étape manuelle :
repasser *Developer mode* sur **Off** et redémarrer. `install.sh` ne modifie rien d'autre sur la TV.

## Aperçu sur ordinateur

Ouvre `index.html` dans Chrome en plein écran (F11). Les flèches et Entrée simulent la télécommande.
Sans la TV, un clic sur une appli affiche seulement un message.
