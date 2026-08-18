[app]

# (str) Titre de votre application
title = Pieces & Consommables

# (str) Nom du paquet (sans espaces ni caractères spéciaux)
package.name = piecesconsommables

# (str) Domaine du paquet (inversé pour l'unicité sur Android)
package.domain = org.maintenance

# (list) Fichiers source à inclure (code python, images, etc.)
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# (list) Application requirements
# Inclut python3, kivy, sqlite3 (intégré nativement), fpdf2 pour les PDF et android pour la gestion des permissions runtime.
requirements = python3,kivy,fpdf2,android

# (str) Version de l'application
version = 1.0

# (list) Orientations supportées
orientation = portrait

# (bool) Indique si l'application doit être en plein écran
fullscreen = 0

# (list) Permissions Android nécessaires pour accéder aux dossiers partagés (Téléchargements / Images)
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# (str) API Android minimale cible
android.minapi = 21

# (str) API Android SDK cible
android.sdk = 33

# (str) Architecture cible (armeabi-v7a et/ou arm64-v8a)
android.archs = arm64-v8a, armeabi-v7a

[buildozer]

# (int) Niveau de log (0 = erreurs uniquement, 1 = infos, 2 = debug)
log_level = 2

# (int) Afficher un avertissement si buildozer est exécuté en root (0 = Non, 1 = Oui)
warn_on_root = 1
