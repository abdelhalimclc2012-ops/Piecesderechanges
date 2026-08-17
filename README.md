# Compiler l'APK "Pieces & Consommables" via GitHub Actions

Aucun PC ni installation nécessaire : GitHub compile l'APK pour toi sur ses
serveurs, tu n'as qu'à téléverser ce dossier.

## Étapes

1. **Créer un compte GitHub** (gratuit) si tu n'en as pas déjà un :
   https://github.com/signup

2. **Créer un nouveau dépôt (repository)** :
   - Va sur https://github.com/new
   - Nom : `piecesconsommables-apk` (ou ce que tu veux)
   - Laisse "Public" ou choisis "Private"
   - Clique "Create repository"

3. **Téléverser les fichiers de ce dossier** dans le dépôt :
   - Sur la page du dépôt, clique "uploading an existing file"
   - Glisse-dépose TOUT le contenu de ce dossier (`main.py`, `buildozer.spec`,
     le dossier `.github` avec `build.yml` dedans)
   - Attention : le dossier `.github/workflows/build.yml` doit garder
     exactement ce chemin (`.github` puis `workflows`), sinon GitHub ne le
     détectera pas comme un workflow. Si le glisser-déposer ne garde pas
     la structure de dossier, utilise plutôt GitHub Desktop ou `git` en
     ligne de commande (voir plus bas).
   - Clique "Commit changes"

4. **Lancer la compilation** :
   - Va dans l'onglet "Actions" du dépôt
   - Le workflow "Build APK" se lance automatiquement après le commit
     (sinon clique dessus puis "Run workflow")
   - La première compilation prend environ 15-25 minutes (elle télécharge
     tout le SDK/NDK Android). Les suivantes seront plus rapides.

5. **Télécharger l'APK** :
   - Une fois le workflow terminé (coche verte), clique dessus
   - En bas de la page, section "Artifacts" : télécharge
     `piecesconsommables-apk`
   - C'est un fichier .zip contenant le .apk — décompresse-le

6. **Installer sur le téléphone** :
   - Transfère le .apk sur ton Honor (câble USB, Drive, etc.)
   - Ouvre-le depuis le gestionnaire de fichiers
   - Autorise "Installer des applications inconnues" si demandé
   - Installe

## Si tu préfères la ligne de commande (git) au lieu du glisser-déposer

```bash
git clone https://github.com/TON_UTILISATEUR/piecesconsommables-apk.git
cd piecesconsommables-apk
# copie main.py, buildozer.spec et .github/ ici
git add .
git commit -m "Premiere version"
git push
```

## Notes

- À chaque modification de `main.py`, un nouveau push relance
  automatiquement la compilation.
- Si le build échoue, l'onglet "Actions" affiche les logs détaillés —
  copie-moi l'erreur et je corrige `buildozer.spec` ou le code en
  conséquence.
- L'app demande les permissions de stockage au premier lancement (pour
  la base SQLite et les exports CSV/PDF) — accepte-les.
