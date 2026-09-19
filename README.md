# invisible_cam

He creado un pequeño proyecto sobre la detección a través del uso de la cámara para ocultar a una persona del plano, sustituyéndola por el fondo que se ha capturado antes.

La idea es sencilla: primero guardas una imagen del fondo, luego cuando alzas el puño o cualquier seña, se detecta a la persona y la reemplaza con esa escena para que parezca que desaparece.

## Qué necesitas

- Python 3.10 o superior
- Webcam
- macOS, Windows o Linux

Las dependencias están en [requirements.txt](requirements.txt).

## Instalar dependencias

Desde la carpeta del proyecto:

```bash
pip install -r requirements.txt
```

Si prefieres crear un entorno virtual antes:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
## Instalación

```bash
git clone [https://github.com/cleonaia/invisible_cam.git](https://github.com/cleonaia/invisible_cam.git)
cd invisible_cam

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Después, abre:

http://127.0.0.1:8000/

## Instalación

```bash
git clone [https://github.com/cleonaia/invisible_cam.git](https://github.com/cleonaia/invisible_cam.git)
cd invisible_cam

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Después, abre:

http://127.0.0.1:8000/

## Ejecutarlo

En tu Mac, la forma correcta es esta:

```bash
cd /Users/leo/Downloads/invisible
/opt/homebrew/Caskroom/miniconda/base/bin/python3 main.py
```

## Cómo usar el proyecto

1. Abre la aplicación.
2. Asegúrate de que la escena esté limpia y sin nadie delante de la cámara.
3. Pulsa "Capturar fondo".
4. La app abrirá una vista previa en vivo con una cuenta atrás. Sal del encuadre antes de que termine.
5. Cuando ya esté capturado el fondo, pulsa "Iniciar aplicación".
6. Alza el puño para activar el efecto.
7. Pulsa "q" para salir de la ventana de cámara.
8. Se recomienda tener buena iluminación para una detección más precisa.

## Archivos importantes

- [main.py](main.py): interfaz principal y flujo de la cámara.
- [invisible.py](invisible.py): lógica del efecto invisible.
- [utils.py](utils.py): detección de personas y estado de la mano.
- [requirements.txt](requirements.txt): dependencias del proyecto.
- [efficientdet_lite0.tflite](efficientdet_lite0.tflite): modelo de detección de personas.
- [hand_landmarker.task](hand_landmarker.task): modelo de detección de manos.

## Nota

La app guarda la imagen de fondo en `invisible.jpg` dentro de la carpeta del proyecto.

Si la cámara no responde, comprueba que no esté siendo usada por otra aplicación.
