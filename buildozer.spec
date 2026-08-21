[app]
title = Gestion Maintenance Delice
package.name = maintenancedelice
package.domain = org.delice
source.dir = .
source.main = main.py
source.include_exts = py,png,jpg,jpeg,ttf,db
version = 2.0
requirements = python3,kivy==2.3.1,fpdf2,fonttools,plyer,Pillow,android
orientation = portrait
fullscreen = 0
icon.filename = %(source.dir)s/iconemaintenance.jpg
android.permissions = VIBRATE
android.api = 33
android.minapi = 21
android.ndk = 25b

# CORRECTIF : arm64-v8a uniquement.
# armeabi-v7a plante systematiquement pendant l'install pip dans un
# venv frais (ImportError: cannot import name 'BuildDependencyInstallError'
# from pip._internal.exceptions) -> bug de compatibilite pip / Python 3.14
# dans l'image Docker actuelle, pas lie a notre code.
# arm64-v8a couvre la quasi-totalite des telephones Android recents
# (ceux depuis ~2019-2020) et s'installe sans probleme (fpdf2 confirme OK).
android.archs = arm64-v8a

android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
