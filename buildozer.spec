[app]

# Titre et package
title = Pieces & Consommables
package.name = piecesconsommables
package.domain = com.hichri.pieces

source.dir =.
source.include_exts = py,png,jpg,jpeg
source.include_patterns = assets/*,images/*
version = 3.0
version.regex = __version__ = ['"](.*)['"]
version.filename = %(source.dir)s/main.py

# Libs
requirements = python3,kivy==2.3.0,fpdf2,Pillow

# Permissions pour Download + choisir un logo
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_IMAGES

# Important pour ton get_export_dir() et get_pictures_dir()
android.request_permissions = 1

[buildozer]

log_level = 2

# --- Android ---
p4a.branch = master
p4a.fork = kivy
p4a.url = https://github.com/kivy/python-for-android.git

android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.accept_sdk_license = True

# Architecture - pour Pydroid / tous les tel
android.archs = arm64-v8a, armeabi-v7a

# Thème
android.theme = Dark
orientation = portrait

# Autoriser l'accès au stockage partagé sur Android 11+
# Sans ça ton export dans /Download va échouer
android.manifest.launch_mode = singleTop
android.wakelock = False
android.allow_backup = True

# Nom de l'apk
# Le fichier final sera dans bin/
# ex: piecesconsommables-3.0-arm64-v8a-debug.apk
p4a.bootstrap = sdl2

# Pour que Kivy ne coupe pas l'interface
kivy.requirements = kivy

# --- iOS (ignoré) ---
[app:ios]
title = Pieces & Consommables
package.domain = com.hichri.pieces
package.name = piecesconsommables
