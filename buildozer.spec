[app]

title = Pieces & Consommables
package.name = piecesconsommables
package.domain = org.monentreprise

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas

version = 1.0

# Dépendances Python nécessaires à l'application.
# sqlite3, os, csv, datetime, contextlib font partie de la
# bibliothèque standard Python -> pas besoin de les lister.
requirements = python3,kivy,fpdf2

orientation = portrait
fullscreen = 0

icon.filename = %(source.dir)s/icon.png

# Permissions Android nécessaires : lecture/écriture stockage
# (export CSV/PDF + choix du logo) et lecture d'images.
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_IMAGES

android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a

# Nécessaire en CI (GitHub Actions) : accepte automatiquement les
# licences du SDK Android, sinon le build s'arrête en attendant une
# confirmation manuelle impossible en environnement non interactif.
android.accept_sdk_license = True

# Nécessaire pour l'accès en écriture aux dossiers publics
# (Download, Pictures...) comme utilisé dans main.py.
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
