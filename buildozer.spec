[app]

title = Pieces & Consommables
package.name = piecesconsommables
package.domain = org.delice

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas

version = 1.0
requirements = python3==3.11.6,hostpython3==3.11.6,kivy==2.3.0,pillow==9.5.0,fpdf2==2.7.9
orientation = portrait 
fullscreen = 0

# Decommente et ajoute icon.png (512x512) a la racine du projet si tu veux une icone perso
# icon.filename = %(source.dir)s/icon.png

android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
