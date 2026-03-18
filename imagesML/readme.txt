Your files should be organized like this
folder
    imagestoML.py
    readme.txt
    requirements.txt (DO NOT OPEN)
    folder (for holding images)
        image1.png
        image2.png
        etc...

right click on the folder for holding images, and choose "Copy as Path"
replace what the variable "foldername" equals with what you have copied

You need python version 3.11.6 - https://www.python.org/downloads/release/python-3116/

Next, change what version of python you are running to 3.11.6
Do this by pressing ctrl+shift+p, and searching for Python: Select Interpreter
Choose 3.11.6

At some point you will be prompted to choose a Virtual Enviroment. Choose venv, and select the file called requirements.txt when prompted. 

Check that your python version is correct by running this command in the terminal
python --version

The first 9 lines, all the imports, will be underlined yellow. To change that, run this command in the terminal
pip install tensorflow keras numpy matplotlib opencv-python
or, run each of these
pip install tensorflow keras
pip install tensorflow-gpu
pip install numpy
pip install matplotlib
pip install opencv

To ensure that you have installed the correct imports, run this command in the terminal
pip list

References:
https://stackoverflow.com/questions/43983718/how-can-i-globally-set-the-path-environment-variable-in-vs-code
https://stackoverflow.com/questions/38896424/tensorflow-not-found-using-pip
https://www.tensorflow.org/install/pip#cpu
https://code.visualstudio.com/docs/python/python-tutorial
