# Gaze - NatHacks 2025
A way to use your computer hands-free through EOG processing and Computer Vision
## Requirements
Install and set up the latest version of [Docker](https://docs.docker.com/get-started/get-docker/).

Alternatively, if you do not want to use Docker, see below for instructions for creating a Python virtual environment.

Clone the repository onto your machine (`git clone https://github.com/arronroasa/gaze-nathacks2025.git`).

This project requires some Python packages as prerequisites.
> If Docker is set up correctly, they should be installed in the docker environment when you execute `run.sh`.
> Alternatively, if you are using the `venv` approach, the packages will be installed directly under the `venv` folder.
```
contourpy==1.3.3
cycler==0.12.1
fonttools==4.60.1
kiwisolver==1.4.9
matplotlib==3.10.7
MouseInfo==0.1.3
numpy==2.2.6
opencv-python==4.12.0.88
packaging==25.0
pandas==2.3.3
pillow==12.0.0
PyAutoGUI==0.9.54
PyGetWindow==0.0.9
PyMsgBox==2.0.1
pyparsing==3.2.5
pyperclip==1.11.0
PyRect==0.2.0
PyScreeze==1.0.1
pyserial==3.5
python-dateutil==2.9.0.post0
pytweening==1.2.0
pytz==2025.2
six==1.17.0
tzdata==2025.2
ultralytics==8.3.226
```
## Using Docker
Once you have cloned the project onto your local machine, open a terminal in the repository folder and run:

```bash
bash ./run.sh
```
> If you are having issues with executing on Linux, try running `chmod +700 setup.sh`.

This should automatically install the dependencies and run the .py file.
## Using the Virtual Environment
If you have decided to use a Python virtual environment, open a `bash` terminal in the project folder and run the following command:
```bash
./setup.sh
```
> If you are having issues with executing on Linux, try running `chmod +700 setup.sh`.

After running `setup.sh`, you can enter the virtual environment by entering `source ./venv/bin/activate`.
> On Windows, it may be `source ./venv/Scripts/activate`.
>
> Additionally on some Linux distributions, you may have to configure `Xauth` in order for pyautogui to work.
## Features
WIP
