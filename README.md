# invisible_cam

I have created a small project that uses the camera to detect and hide a person from the frame, replacing them with the background captured beforehand.

The idea is simple: first, you save an image of the background. Then, when you raise your fist or make another gesture, the person is detected and replaced with that scene, making it look as if they have disappeared.

## Requirements

- Python 3.10 or higher.
- A webcam.
- macOS, Windows, or Linux.

The dependencies are listed in [`requirements.txt`](https://github.com/cleonaia/invisible_cam/blob/main/requirements.txt).

## Installing the dependencies

From the project directory:

```bash
pip install -r requirements.txt
```

If you prefer to create a virtual environment first:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Installation

```bash
git clone https://github.com/cleonaia/invisible_cam.git
cd invisible_cam

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Then open:

[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Running the project

On your Mac, the correct way to run it is:

```bash
cd /Users/leo/Downloads/invisible
/opt/homebrew/Caskroom/miniconda/base/bin/python3 main.py
```

## How to use the project

1. Open the application.
2. Make sure the scene is clear and that nobody is in front of the camera.
3. Click **“Capture Background”**.
4. The app will open a live preview with a countdown. Move out of the frame before the countdown ends.
5. Once the background has been captured, click **“Start Application”**.
6. Raise your fist to activate the effect.
7. Press **“q”** to close the camera window.

Good lighting is recommended for more accurate detection.

## Important files

- [`main.py`](https://github.com/cleonaia/invisible_cam/blob/main/main.py): Main interface and camera workflow.
- [`invisible.py`](https://github.com/cleonaia/invisible_cam/blob/main/invisible.py): Logic behind the invisible effect.
- [`utils.py`](https://github.com/cleonaia/invisible_cam/blob/main/utils.py): Person detection and hand-state detection.
- [`requirements.txt`](https://github.com/cleonaia/invisible_cam/blob/main/requirements.txt): Project dependencies.
- [`efficientdet_lite0.tflite`](https://github.com/cleonaia/invisible_cam/blob/main/efficientdet_lite0.tflite): Person-detection model.
- [`hand_landmarker.task`](https://github.com/cleonaia/invisible_cam/blob/main/hand_landmarker.task): Hand-detection model.

## Note

The app saves the background image as `invisible.jpg` inside the project directory.

If the camera does not respond, check that it is not being used by another application.

## ⭐ Support the project

If you found this project useful, if it helped you learn, or if you simply enjoyed it, please give this repository a star ⭐ on GitHub.

Your star helps the project reach more people and motivates me to keep improving it!

Thank you for your support! 🙌
