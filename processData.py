# Ryan Kaczur

import matplotlib.pyplot as plt

def findCurrentStackSizes(definedSizesStr:str, debugging:bool) -> dict:

    """
    Takes a portion of code from the MSB config file and extracts the size of the memory allocated to each thread's stack

    Args:
    definedSizesStr - the portion of code from the MSB
    debugging - if True this function prints extra information so users can see where things fail

    Returns:
    DefinedStackSizesDict - a dictionary with an item for each thread, the values are ints and describes the memory allocated to each thread
    """

    DefinedStackSizesDict = {}
    for line in definedSizesStr.split("#"):
        if debugging: print(line)
        if "//" not in line: continue
        defines = line.split("//")
        if debugging: print(defines)
        defines[0] = defines[0][defines[0].index("_SIZE ")+6:].split("*")
        product = 1
        for num in defines[0]:
            product *= int(num.strip())
        DefinedStackSizesDict[defines[1].strip()] = product

    if debugging: print(f"DefinedThreadSizes: \n{DefinedStackSizesDict}")

    return DefinedStackSizesDict


def processData(DefinedStackSizesDict:dict, OutputDataFile:str, debugging:bool, msg:str) -> dict:

    """
    Takes the raw data and creates a dictionary with an item for each thread with a list of every data point as an intager

    Args:
    DefinedStackSizesDict - dictionary of allocated memory to each thread
    OutputDataFile - name of the file to read
    debugging - if True this function prints extra information so users can see where things fail
    msg - describes the format of the serial output

    Returns:
    CleanData:dict - an item for each thread with a list of every data point as an intager
    MaximumUsedSpace:dict - an item for each thread with an interger showing the maximum used memory by the thread that was observed by the program
    """

    CleanData = {}

    with open(OutputDataFile, mode="r", errors='ignore') as rawData: 
        for line in rawData:
            if msg not in line:
                if debugging: print(f"Skipped line:\n{line}")
                continue
            try:
                name, value = line.strip().split(":")
                name = name[name.rindex(msg) + len(msg):]
                value = int(value[1:])
                if name not in CleanData:
                    if name in DefinedStackSizesDict:
                        CleanData[name] = [value]
                    else:
                        if debugging: print(f"Skipped line:\n{line}")
                else:
                    CleanData[name] += [value]
            except Exception as e:
                if debugging: print(f"Skipped line: {e}\n{line}")
                continue

    if debugging: print(f"cleaned data from file: the keys are the thread names the value is a list of the {CleanData}")

    MaximumUsedSpace = {thread:0 for thread in DefinedStackSizesDict.keys()}

    # Finding the maximums of the used stack space
    for thread, values in CleanData.items():
        for val in values:
            if DefinedStackSizesDict[thread] - val > MaximumUsedSpace[thread]:
                MaximumUsedSpace[thread] = DefinedStackSizesDict[thread] - val

    if debugging: print(MaximumUsedSpace)

    return CleanData, MaximumUsedSpace


def plotCleanData(CleanData:dict, DefinedThreadSizes:dict, OutputDataFile:str) -> None:

    """
    Plots the data

    Args: 
    CleanData:dict - thread_name:[unused space]
    DefinedThreadSizes:dict - thread_name:size_of_Allocted_memory
    OutputDataFile:str - for titling the graph

    Returns: None
    """
    
    colors = ["red", "blue", "green", "yellow", "brown", "orange", "cyan", "black"]

    plt.ylim(-10, 1100)  # max value is roughly 100 larger than greatest assigned stack size

    i = 0
    for thread, values in CleanData.items():
        # plt.plot(values, label=f"{thread} unused space", linestyle = "--", color = colors[i])
        plt.plot([DefinedThreadSizes[thread] - val for val in values], label=f"{thread} used space", linestyle = "-", color = colors[i])
        plt.plot([DefinedThreadSizes[thread] for _ in values], label=f"{thread} Max space", linestyle = ":", color = colors[i])
        i += 1

    # plt.grid()
    plt.xlabel("Timer ticks")
    plt.ylabel("Bytes")
    plt.title(OutputDataFile)
    plt.legend()
    plt.show()


def createNewStackSizes(MaximumUsedSpace:dict) -> str: #And file
    """Takes the MaximumUsedSpace dictionary
    Returns a string of reccomended stack sizes to try and creates a file with the stack sizes and their corresponding threads to be copied"""
    result = ""
    with open("NewStackSizes.txt", mode='w') as resultFile:
        for thread, stackSize in MaximumUsedSpace.items():     
            # +20 comes from the 20 byte signature that the hardware uses to check for stack overflow
            result += f"For thread {thread} use \t{stackSize + 20}\tbytes"
            resultFile.write(f"{stackSize + 20}\t//{thread}\n")
    return result