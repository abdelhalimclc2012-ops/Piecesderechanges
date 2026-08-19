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
# python3/hostpython3 pinnes a 3.11.6 : la derniere version (3.14) casse la
# compilation de Kivy et le module fpdf2 n'a pas de wheel Android sur PyPI.
# fpdf2 n'est PAS liste ici : son code est copie directement dans le dossier
# fpdf/ a cote de main.py (bundle en tant que source, pas via pip).
# "android" n'est pas non plus un requirement : le support Android est
# automatiquement inclus par python-for-android.
requirements = python3==3.11.6,hostpython3==3.11.6,kivy==2.3.0,pillow==9.5.0

# (str) Version de l'application
version = 1.0

# (list) Orientations supportées
orientation = portrait

# (bool) Indique si l'application doit être en plein écran
fullscreen = 0

# (list) Permissions Android nécessaires pour accéder aux dossiers partagés (Téléchargements / Images)
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE

# (str) API Android minimale cible
android.minapi = 21

# (str) API Android SDK cible
android.api = 33

# (str) Version du NDK Android (pinnee pour la reproductibilite du build)
android.ndk = 25b

# (str) Architecture cible (armeabi-v7a et/ou arm64-v8a)
android.archs = arm64-v8a, armeabi-v7a

# (bool) Accepter automatiquement les licences du SDK Android (evite un blocage interactif)
android.accept_sdk_license = True

[buildozer]

# (int) Niveau de log (0 = erreurs uniquement, 1 = infos, 2 = debug)
log_level = 2

# (int) Afficher un avertissement si buildozer est exécuté en root (0 = Non, 1 = Oui)
warn_on_root = 1
