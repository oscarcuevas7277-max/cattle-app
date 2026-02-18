[app]
title = Gestion Ganadera PRO
package.name = ganaderiapr
package.domain = com.ganaderia
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy==2.2.1,sqlite3,pillow
orientation = portrait
fullscreen = 0
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 31
android.minapi = 21
android.ndk = 23b
android.private_storage = True
android.archs = arm64-v8a
android.allow_backup = True
android.logcat_filters = *:S python:D
android.copy_libs = 1

[buildozer]
log_level = 2
warn_on_root = 1
