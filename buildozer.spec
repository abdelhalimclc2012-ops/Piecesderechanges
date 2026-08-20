[app]

# Titre et package
title = Pieces & Consommables
package.name = piecesconsommables
package.domain = com.hichri.pieces

source.dir = .
source.include_exts = py,png,jpg,jpeg
source.include_patterns = assets/*,images/*
version = 3.0

# Libs
requirements = python3==3.11,hostpython3==3.11,kivy==2.3.0,fpdf2,Pillow

# Permissions pour Download + choisir un logo
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_IMAGES

# Important pour ton get_export_dir() et get_pictures_dir()
android.request_permissions = 1

# IMPORTANT : cette option doit etre dans [app], pas dans [buildozer],
# sinon buildozer ne l'applique pas et le build reste bloque sur
# l'acceptation manuelle de la licence du SDK (impossible en CI).
android.accept_sdk_license = True

android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33

# Architecture - pour Pydroid / tous les tel
android.archs = arm64-v8a, armeabi-v7a

# Theme
android.theme = Dark
orientation = portrait

# Autoriser l'acces au stockage partage sur Android 11+
# Sans ca ton export dans /Download va echouer
android.manifest.launch_mode = singleTop
android.wakelock = False
android.allow_backup = True

# Nom de l'apk
# Le fichier final sera dans bin/
# ex: piecesconsommables-3.0-arm64-v8a-debug.apk
p4a.bootstrap = sdl2

[buildozer]

log_level = 2

# --- Android ---
# (p4a.branch/fork/url volontairement retires : on laisse buildozer
# utiliser sa version stable de python-for-android par defaut,
# au lieu de "master" qui est la branche de developpement instable
# et qui causait l'echec pip/Python 3.14 des builds precedents)

# --- iOS (ignore) ---
[app:ios]
title = Pieces & Consommables
package.domain = com.hichri.pieces
package.name = piecesconsommables
