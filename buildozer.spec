[app]
title = Gestion Ganadera PRO
package.name = ganaderiapr
package.domain = com.ganaderia
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0

# CORREGIDO: Especificar versión de Python y agregar pyjnius compatible
requirements = python3==3.10.11,kivy==2.2.1,pillow,pyjnius==1.5.0

# Opciones de UI
orientation = portrait
fullscreen = 0

# Permisos Android
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Versión de API Android
android.api = 31
android.minapi = 21

# NDK - Actualizado a versión más estable
android.ndk = 25b

# Almacenamiento privado
android.private_storage = True

# Arquitectura
android.archs = arm64-v8a

# Backup y logs
android.allow_backup = True
android.logcat_filters = *:S python:D

# AGREGADO: Copiar librerías necesarias
android.copy_libs = 1

# AGREGADO: Configuración para evitar problemas de Cython
android.gradle_dependencies = 

# AGREGADO: Aumentar timeouts para descargas
p4a.timeout = 20

# AGREGADO: Usar bootstrap SDL2 con pyjnius
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1

# AGREGADO: Más información de depuración
# log_level = 2 mostrará logs detallados
