Copy in your output.txt to the same directory run StackOptimizationHelper.py step '4' and '5' if you feel like it


The stack sizes of the threads are assigned within osThreadAttr_t objects (.stack_size) in units of bytes 
You can get the space remaining with a rtos function (osThreadGetStackSpace) also in bytes (https://arm-software.github.io/CMSIS_6/latest/RTOS2/group__CMSIS__RTOS__ThreadMgmt.html#ga9c83bd5dd8de329701775d6ef7012720)

so to get the stack space that the thread is actually using subtract the stack space from the .stack_size.

FreeRTOS checks the top 20 bytes of the stack to check for overflow. so osThreadGetStackSpace() needs to be atleast 20 to not get the overflow message.

As a 2140 project I wrote some python that makes a graph of the data over time. I had a timer printf out the stack space every tick, probably not ideal. If you want to use it call ner serial > output.txt move the output file into the folder of the program and start at step '4'. (https://github.com/RyanK952/Stack-Size-Monitoring-on-NER-boards--2140-Project)
