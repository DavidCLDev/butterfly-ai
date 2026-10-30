# Vanartia 🦋

Aplicación Django para registrar avistamientos de mariposas. Al subir una
fotografía, el modelo `clasificador_web/model/best.onnx` identifica el género
y la aplicación conserva la imagen, el resultado y su confianza en la galería
privada del usuario.

## Ejecutar localmente

Desde la raíz del repositorio, instala las dependencias e inicia el servidor:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r .\clasificador_web\requirements.txt
cd .\clasificador_web
python manage.py migrate
python manage.py runserver
```

Registra una cuenta en `/registrar/` e inicia sesión. Las imágenes se guardan
en `clasificador_web/media/` durante el desarrollo. El modelo usa ONNX Runtime
en CPU y las etiquetas incluidas en sus metadatos: Anartia, Ascia, Battus,
Danaus, Dryas, Heliconius, Morpho, Papilio, Phoebis y Vanessa.

Para ejecutar las pruebas:

```powershell
python manage.py test
```
