# Ryan Kaczur

import usb.core
import usb.util

def showAllDevices() -> str:
    """
    Args: None\t\tReturns: str
    Returns a string of all devices that pyusb can detect, good way to see if pyusb is setup properly
    """
    devList = usb.core.find(find_all=True)
    output = ""
    for device in devList:
        output += str(device) + "\n"
    return output

def selectDevice(hexIdVendor:int, hexIdProduct:int) -> None:
    """
    Displays all the information of the device,
    Most importantly this function displays the configurations of the device and displays its endpoints which are inportant for sending a reiceiving data with the device

    Args:
    hexIdVendor, hexIdProduct - the IDs of the USB device to be connected
    Returns: None
    """
    dev = usb.core.find(idVendor = hexIdVendor, idProduct = hexIdProduct)

    print(str(dev), "\n\n")

    # usb configurations and interfaces are standardized and have numbers assigned to them, this library 
    for cfg in dev:     # usb configuration 
        print(f"USB Configuration:\n{cfg.bConfigurationValue}")
        print("\tUSB interfaces:")
        for intf in cfg:        # usb interfaces for each usb configuration
            print(f"\t{intf.bInterfaceNumber}, {intf.bAlternateSetting}")
            print("\t\tEnd Points:")
            for ep in intf:     # end points needed to know when the device is sending and receiving data
                print(f'\t\t{ep.bEndpointAddress}')


def readSerialOutput(hexIdVendor:int, hexIdProduct:int, numOfBytes:int, timeOut:int, debugging:bool, filename:str) -> int:
    """
    Creates a file from the serial output of the usb device

    Args:
    hexIdVendor:int, hexIdProduct:int - device IDs
    numOfBytes:int, the amount of data to collect in bytes
    timeOut:int - the time to wait for data collection in ms
    debugging:bool - if True this function prints extra information so users can see where things fail
    filename:str - The file name to copy the serial output into

    Returns:
    intager - error code, 0-no error, >0-error
    """

    dev = usb.core.find(idVendor = hexIdVendor , idProduct = hexIdProduct)

    if dev is None:
        print("Failed to create USB device object")
        return 1

    endpoints = []

    for cfg in dev:
        if debugging: print(str(cfg.bConfigurationValue) + '\n')
        for intf in cfg:
            if debugging: print('\t' + str(intf.bInterfaceNumber) + ',' + str(intf.bAlternateSetting) + '\n')
            USBInterfaceValues = [intf.bInterfaceNumber, intf.bAlternateSetting]
            for ep in intf:
                if debugging: print('\t\t' + str(ep.bEndpointAddress) + '\n')
                endpoints += [ep.bEndpointAddress]

    dev.set_configuration() #sets usb configuration to the first one, in the MSB's case, the only one, in code

    # similarly sets usb interface
    dev.set_interface_altsetting(interface = USBInterfaceValues[0], alternate_setting = USBInterfaceValues[1])

    if debugging: print(f"Using end point: {endpoints[0]}") #used for usb bulk transfer protocol, which is what serial output is
    # exact specifications for the board and serial output couldn't be found so the large numbers: 10000000000, 100000 were frequently used for numofBytes and timeOut
    ret = dev.read(endpoints[0], numOfBytes, timeOut) # timeOut[ms] describes how long the program will wait for the num of bytes to be filled in milliseconds
    # ret is an array
    if debugging: print(f"Array ret: {ret}")

    if debugging:
        charactersInRet = {}
        for x in ret:
            if chr(x) not in charactersInRet:
                charactersInRet[chr(x)] = 1
            else:
                charactersInRet[chr(x)] += 1
        print(charactersInRet)

    with open(filename, mode='w', encoding="utf-8") as outputFile: #encoding="utf-8"
        if debugging: print(''.join([chr(x) for x in ret if (x == 2 or x == 13 or x == 96 or chr(x) == 'b') == False]))
        outputFile.write(''.join([chr(x) for x in ret if (x == 2 or x == 13 or x == 96 or chr(x) == 'b') == False]))
        # if statement required because USB protocol generates them and they will create errors at chr(), bs also pop up

    # Closing connection, allows the program to swtich the usb device back to WSL
    dev.reset()
    usb.util.dispose_resources(dev)

    return 0