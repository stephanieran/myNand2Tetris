from clean import clean
from Translator import *
import os
import sys

# driver of the translator.py program

inFiles = []
inPath = sys.argv[1]

if os.path.isfile(inPath) and inPath[-3:] == ".vm": # file
    inFiles.append(inPath)
    outFile = inPath[:-3] + ".asm"
elif os.path.isdir(inPath): # directory
    if inPath[-1:] == "/":
        inPath = inPath[:-1]
    for file in os.listdir(inPath):
        if file[-3:] == ".vm":
            inFiles.append(inPath + "/" + file)
    outFile = inPath + ".asm"

outLinesFinal = []

def writeAsm(filePathName):
    vmLines = clean(filePathName) # returns the cleaned up list of lines
    jumpLabelCounter = 0
    funcLabelCounter = 1
    outLines = []

    for line in vmLines:
        tempList = line.split() # split the line of text and save into temp list
        argNum = len(tempList)
        if argNum == 1: # arithmetic or jump command
            if tempList[0] in ["add", "sub", "and", "or", "neg", "not"]:
                linesToAppend = arithmetic_command(tempList[0])
            elif tempList[0] in ["eq", "lt", "gt"]:
                jumpLabelCounter, linesToAppend = jump_command(tempList[0], jumpLabelCounter)
            elif tempList[0] == "return":
                linesToAppend = funcReturn()
            else:
                print("Command not in arithmetic command symbols or Return.")
            for line in linesToAppend:
                outLines.append(line)
        elif argNum == 2:
            if tempList[0] == "if-goto":
                linesToAppend = ifGoTo(tempList[1])
            elif tempList[0] == "goto":
                linesToAppend = goTo(tempList[1])
            elif tempList[0] == "label":
                linesToAppend = label(tempList[1])
            else:
                print("Command not if-goto, goto, or label.")
            for line in linesToAppend:
                outLines.append(line)
        elif argNum == 3:
            if tempList[0] == "push":
                linesToAppend = push(tempList[1], tempList[2], filePathName)
            elif tempList[0] == "pop":
                linesToAppend = pop(tempList[0], tempList[1], tempList[2], filePathName)
            elif tempList[0] == "function":
                linesToAppend = funcDef(tempList[1], tempList[2])
            elif tempList[0] == "call":
                funcLabelCounter, linesToAppend = funcCall(tempList[1], tempList[2], funcLabelCounter)
            for line in linesToAppend:
                outLines.append(line)
        else:
            print("Unable to append, incorrect number of arguments for the command")
        
    return outLines


# write bootstrap code
toAppend = init(0)
for line in toAppend:
    outLinesFinal.append(line)

for inFileName in inFiles:
    outLinesadd = writeAsm(inFileName)
    for line in outLinesadd:
        outLinesFinal.append(line)

counter = 1
for line in outLinesFinal:
    print(line)
    counter +=1

# write asm code to outFile
with open(outFile, 'w') as OF:
    for line in outLinesFinal:
        OF.write(line + '\n')