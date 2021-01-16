# ALEAPP
Android Logs Events And Protobuf Parser

Details in blog post here: https://abrignoni.blogspot.com/2020/02/aleapp-android-logs-events-and-protobuf.html  

## Requirements
**Python 3.9 or above** (older versions of 3.x will also work with the exception of one or two modules)

### Dependencies

Dependencies for your python environment are listed in `requirements.txt`. Install them using the below command. Ensure the `py` part is correct for your environment, eg `py`, `python`, or `python3`, etc. 

`py -m pip install -r requirements.txt`  
or  
 `pip3 install -r requirements.txt`

To run on **Linux**, you will also need to install `tkinter` separately like so:

`sudo apt-get install python3-tk`

To install dependencies offline Troy Schnack has a neat process here:
https://twitter.com/TroySchnack/status/1266085323651444736?s=19

## Usage

### CLI

```
$ python aleapp.py -t <zip | tar | fs | gz> -i <path_to_extraction> -o <path_for_report_output>
```

### GUI

```
$ python aleappGUI.py 
```

### Help

```
$ python aleapp.py --help
```

## Acknowledgements

This tool is the result of a collaborative effort of many people in the DFIR community.