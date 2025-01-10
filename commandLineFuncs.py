# Ryan Kaczur

import subprocess

def attachUSBDeviceToWSL(busid:str) -> str:
    """
    Calls "usbipd attach" in a windows terminal allowing WSL to flash code to the board

    Args: busid - str
    Returns: output - str
    """
    try:
        result = subprocess.run(f"usbipd attach --wsl --busid={busid}", shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            output = f"Failed to attach device to WSL\nError: {result.stderr.strip()}"
        else: 
            output = "Attached device succsefully:\n" + result.stdout.strip()
    except Exception as e:
        output = f"Failed to attach device to WSL\nPython Error: {e}"
    return output

def detachUSBDeviceFromWSL(busid:str) -> str:
    """
    Calls "usbipd detach" in a windows terminal allowing WSL to flash code to the board

    Args: busid - str
    Returns: output - str
    """
    try:
        result = subprocess.run(f"usbipd detach --busid {busid}", shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            output = f"Failed to detach device from WSL\nError: {result.stderr.strip()}"
        else: 
            output = "Detached device succsefully:\n" + result.stdout.strip()
    except Exception as e:
        output = f"Failed to detach device from WSL\nPython Error: {e}"
    return output

def UsbipdList() -> str:
    """
    Runs usbipd list in a windows terminal returns the output or errors in a string
    Returns: output - str
    """
    try:
        # Show all usb devices that windows can see
        result = subprocess.run("usbipd list", shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            output = "usbipd list:\n" + str(result.stdout)
        else:
            output = f"Command line Error: {result.stderr.strip()}"
    except Exception as e:
        output = f"Python Error: {e}"
    return output