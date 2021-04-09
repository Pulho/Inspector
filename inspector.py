import os
import sys
from classes.png import PNG

class File:
    def __init__ (self, name, hexList, fileSize, parameters):
    # Signature propriety
        self.hex            = hexList
        self.parameters     = parameters

    # File propriety
        self.type           = ""
        self.name           = name
        self.bytes          = fileSize

# Return functions

    # retSize: Function to return the bytes size of the file
    def retSize(self):
        return self.bytes

    # retName: Function to return the file name
    def retName(self):
        return self.name

    # retParameters: Function to return file parameters
    def retParameters(self):
        return self.parameters

# Set functions
    
    # setType: Stores the current file type
    def setType(self, name):
        self.type = name

    # details: Shows the information collected from the analyzed file
    def details(self, img):
        print(f"Showing file Propriety:\nChunks Order: {img.retOrder()}\nDimension: {img.retDimension()}")
        print(img.retData())

# checkFile: Treats the file according to the magic bytes found (Currently only treats PNG)
def checkFile(file, fixFile=False, forceType=None):
    if forceType != None:
        forceType = forceType.lower()
        if forceType == 'png': # Forces the type to PNG, now the file will be treated as one
            file.setType("Force type: PNG")
            Png = PNG(file.retName(), fixFile)
            Png.info()
            file.details(Png)
        else: 
            print('Type not recognized')
    else:     
        if file.hex[:8] == ['89','50','4e','47','0d','0a','1a','0a']: # Checks whether the bytes are corresponding with a PNG file
            file.setType("PNG")
            Png = PNG(file.retName(), fixFile)
            Png.info()
            file.details(Png)
        else:
            print('Magic bytes not recognized')

# help: Help function that explains how the script works and its parameters
def help(func=None):
    if func == None:
        print("Usage:\n\tinspector [OPTIONS] [FILE]")
        print("\nOptions:\n\t-ff, --fixfile:\n\t\tTry to fix file bytes (Recommended to backup the file before)\n\n\t-ft=<extension>, --forcetype=<extension>:\n\t\tTreat the file as input type\n")
    return

# checkParameters: Function that is intended to check the parameters passed to the script and treat them
def checkParameters(file, size):
    ft = None # By default, ft (force type) come as None
    ff = False # By default ff (fix file) come as False
    parameters = file.retParameters()

    for i in range(size):
        # Help
        if parameters[i] == "--help" or parameters[i] == "-h":
            help()
            exit()
        # Fix file
        elif parameters[i] == "-ff":
            ff = True
        elif parameters[i] == "--fixfile":
            ff = True
        # Force type
        elif parameters[i][:4] == "-ft=":
            ft = parameters[i][4:]
        elif parameters[i][:12] == "--forcetype=":
            ft = parameters[i][12:]
        else:
            print(f"INPUT ERROR: Parameter '{parameters[i]}' Not recognized")
            exit()                  
    checkFile(file=file, fixFile=ff, forceType=ft)

# sigFile: Initial scan to find out the magic bytes of the file along with its size in bytes
def sigFile(filename, parameters):
    fileObject  = open(filename, "rb")
    headerBytes = []
    
    content = fileObject.read(16).hex()
    for i in range(0,len(content),2):
        hexValue = hex(int("0x" + content[i:i+2], 16))
        if len(hexValue) == 3:
                hexValue = "0" + hexValue[-1:]
        else:
            hexValue = hexValue[-2:]
        headerBytes.append(hexValue)

    size = os.stat(filename).st_size
    file = File(name=filename, hexList=headerBytes, fileSize=size, parameters=parameters)
    fileObject.close()

    checkParameters(file, len(file.retParameters()))

def main(): 
    if len(sys.argv) < 2:
        help()
        return
    elif len(sys.argv) == 2 and ( sys.argv[1] == '--help' or sys.argv[1] == '-h'):
        help()
        return
    sigFile(sys.argv[-1:][0], sys.argv[1:-1]) # First argument represents the filename and the second one its parameters
main()
