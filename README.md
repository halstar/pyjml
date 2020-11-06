# pyjml
A based Python-based tool to import Joomla articles from version 1.5 to 3.9.

Used one shot. Written from scratch. Sharing here as I would have appreciated starting from a project like this one

## Prerequisites

This project requires to have Python 3 installed on your computer. 

## Getting Started

### Linux

If not already available, you will be likely to install Python like this:
```
$ sudo apt-get update
$ sudo apt-get install python3.6
```

Then simply call pyjml/pyjml.py from the command line and start playing with options:
```
python3 pyjml.py --help
```

### Windows

You will have to download and install the latest Python 3 package from [python.org](https://www.python.org/downloads/windows/)

Then, locate where python.exe was installed, e.g. under: C:\Users\JohnDoe\AppData\Local\Programs\Python\Python36-32, open a command prompt, get there and call pyjml/pyjml.py via python.exe:
```
C:\Users\JohnDoe>`
C:\Users\JohnDoe>cd AppData\Local\Programs\Python\Python36-32
C:\Users\JohnDoe\AppData\Local\Programs\Python\Python36-32>python.exe C:\Users\JohnDoe\pyjml\pyjml.py --help
```