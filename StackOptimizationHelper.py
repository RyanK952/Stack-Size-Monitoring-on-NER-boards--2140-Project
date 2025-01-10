# Ryan Kaczur

import os
import time

import collectData
import processData
import commandLineFuncs as cl

rawDataFileName = None
hexIdVendor, hexIdProduct = (None, None)
busid = None

# User interface functions
def getDeviceIDs() -> int:
    """
    Gets the Vendor ID and Product ID, handles converting strings into hexadecimal numbers if needed.
    Gracefully handles errors
    
    Returns:
    hexIdVendor:int
    hexIdProduct:int
    """
    while(True):
        hexIdVendor = input("Vendor ID in Hex: ")
        if hexIdVendor == "":
            hexIdVendor = 0x0403
            break
        else:
            try:
                hexIdVendor = int(hexIdVendor, 16)
                break
            except Exception as e:
                print(f"Not a vaild input, Error: {e}")
                print("Try again")

    while(True):
        hexIdProduct = input("Product ID in Hex: ")
        if hexIdProduct == "":
            hexIdProduct = 0x6010
            break
        else:
            try:
                hexIdProduct = int(hexIdProduct, 16)
                break
            except Exception as e:
                print(f"Not a vaild input, Error: {e}")
                print("Try again")

    return hexIdVendor, hexIdProduct

def getDebugMode() -> bool:
    """
    Prompts user if they would like to have extra print outs
    Returns: bool
    """
    debugging = input("Debug mode?: ").lower()
    return debugging == 'y' or debugging == "yes" or debugging == 't' or debugging == 'true'

def getRawDataFileName(rawDataFileName:str) -> str:
    """
    Gets the name of the file to write the readable output of the serial communication of the Board
    Args: Current rawDataFileName - str
    Returns: rawDataFileName - str
    """
    if rawDataFileName == None:
        rawDataFileName = input("Enter the file name of the output data (No .txt)\nOr enter nothing for default: ")
        if rawDataFileName == "":
            rawDataFileName = "output.txt"
        else:
            rawDataFileName = rawDataFileName + ".txt"
    else:
        storedFileName = rawDataFileName
        rawDataFileName = input("Enter the file name of the output data (No .txt)\nOr enter nothing for default\nOr enter 's' for the stored value: ")
        if rawDataFileName == "":
            rawDataFileName = "output.txt"
        elif rawDataFileName == "s":   #s for same
            rawDataFileName = storedFileName
        else:
            rawDataFileName = rawDataFileName + ".txt"
    return rawDataFileName

# Code begins
while(True):
    print("--- Stack Optimization Helper ---")
    print("Enter one of the following commands to continue")
    print("\t\'1\' - see connected devices")
    print("\t\'2\' - select device")
    print("\t\'3\' - collect data")
    print("\t\'4\' - process data")
    print("\t\'5\' - create new stack sizes")
    print("\t\'e\' - exit")
    userInput = input("--> ").lower()
    
    if userInput == 'e':
        print("Terminating")
        break
    elif userInput == '1':      # select a device
        print("Make sure the device is connected")

        checkingUsersResolve = input("Proceed? [y/n] ")
        if checkingUsersResolve == "n":
            continue
        
        print(cl.UsbipdList())

        busid = input("Select a device by entering it's bus id (1-#): ")
        if busid == "":
            busid = "1-9"
        # Default value

        # this command prints errors if the bus id is wrong
        print(cl.detachUSBDeviceFromWSL(busid))

        # this shows all the devices that pyusb can see
        print(collectData.showAllDevices())
    elif userInput == '2':
        print("make sure the device is connected")

        print(collectData.showAllDevices())

        hexIdVendor, hexIdProduct = getDeviceIDs()

        print("\n\nThe selected device:\n")
        collectData.selectDevice(hexIdVendor, hexIdProduct)

    elif userInput == '3':

        # If step 1 is skipped
        if busid == None:
            busid = busid = input("Select a device by entering it's bus id (1-#): ")
            if busid == "":
                busid = "1-9"

        # If step 2 is skipped
        if hexIdVendor == None or hexIdProduct == None:
            hexIdVendor, hexIdProduct = getDeviceIDs()
        
        rawDataFileName = getRawDataFileName(rawDataFileName)

        while(True):
            numOfBytes = input("Number of bytes to record: ")
            if numOfBytes == "":
                numOfBytes = 10000000000
                break
            else:
                try:
                    numOfBytes = int(numOfBytes)
                    break
                except:
                    print("That was not a interger try again or don't enter anything")

        while(True):
            timeOut = input("How long to wait for the data: ")
            if timeOut == "":
                timeOut = 100000
                break
            else:
                try:
                    timeOut = int(timeOut)
                    break
                except:
                    print("That was not a interger try again or don't enter anything")

        debugging = getDebugMode()

        print(cl.attachUSBDeviceToWSL(busid))

        print("Modifications to MSB code should be saved now")
        checkingUsersResolve = input("Proceed? [y/n] ")
        if checkingUsersResolve == "n":
            continue

        # WSL NER commands
        print("run this in a wsl terminal, your path may be different:\ncd ~ && cd NER/MSB-FW/ && nervenv && ner build && ner flash --ftdi && timeout 0.2 ner serial")
        checkingUsersResolve = input("\nProceed? (answer quickly after command completes for best results) [y/n] ")
        if checkingUsersResolve == "n":
            continue

        print(cl.detachUSBDeviceFromWSL(busid))

        # Wait for windows to switch device from WSL back to windows
        time.sleep(1)

        print("Collecting data ...")
        if collectData.readSerialOutput(hexIdVendor, hexIdProduct, numOfBytes, timeOut, debugging, rawDataFileName) == 0:
            print(f"Done! check {rawDataFileName}\n")

        print(cl.attachUSBDeviceToWSL(busid))

    elif userInput == '4':

        rawDataFileName = getRawDataFileName(rawDataFileName)
        if not os.path.exists(rawDataFileName):
            print(f"Couldn't find file with the name: {rawDataFileName}")
            continue

        definedSizesStr = input("paste in the #defines from the msb_config.h file (as one line when propted): \n")
        if definedSizesStr == "":
            definedSizesStr = """#define DEFAULT_TASK_STACK_SIZE 16 //defaultTaskHandle         //128 * 4        //+16
#define CAN_DISPATCH_STACK_SIZE 128 * 8 //can_dispatch_handle       //128 * 8
#define LED_CONTROLLER_STACK_SIZE 124 //led_controller_handle    //32 * 8   //+16
#define TEMP_MONITOR_STACK_SIZE 404 //temp_monitor_handle    //64 * 8   //+16
#define IMU_MONITOR_STACK_SIZE 64 * 8 //imu_monitor_handle      //not connected
#define TOF_MONITOR_STACK_SIZE 128 * 8 //tof_monitor_handle     //not connected
#define SHOCKPOT_MONITOR_STACK_SIZE 220 //shockpot_monitor_handle    //64 * 8  //+16
#define STRAIN_MONITOR_STACK_SIZE 236 //strain_monitor_handle    //64 * 8    //+16"""

        debugging = getDebugMode()

        DefinedStackSizesDict = processData.findCurrentStackSizes(definedSizesStr, debugging)

        msg = input("Enter the string that appears before the thread name in the output\nYou may need to check the output file\nEnter nothing for default: ")
        if msg == "":
            msg = "Unused stack space of "

        CleanData, MaximumUsedSpace = processData.processData(DefinedStackSizesDict, rawDataFileName, debugging, msg)
        
        processData.plotCleanData(CleanData, DefinedStackSizesDict, rawDataFileName)
        
    elif userInput == '5' and 'MaximumUsedSpace' in globals():
        print(processData.createNewStackSizes(MaximumUsedSpace))
    elif userInput == '5':
        print("Please run command '4' first")
    else:
        print("Try again")
