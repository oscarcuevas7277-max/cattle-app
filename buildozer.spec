[app]
title = Gestion Ganadera PRO
package.name = ganaderiapr
package.domain = com.ganaderia
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.1

# CORRECCIÓN IMPORTANTE: agregar pyjnius para Android
requirements = python3,kivy==2.1.0,android,pyjnius

orientation = portrait
fullscreen = 0

# Permisos necesarios
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,INTERNET

android.api = 31
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a
android.allow_backup = True

# IMPORTANTE: Copiar sqlite3
android.add_src = 

# Logs para debug
android.logcat_filters = *:S python:D

[buildozer]
log_level = 2
warn_on_root = 0
