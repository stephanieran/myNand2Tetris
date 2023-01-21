from clean import clean
from vmTranslations import oneArgNEW, threeArgNEW
import os
import sys
# this program cleans the .vm file of any whitespaces/comments and writes
# the translated asm code to a .asm output file.

filepath = sys.argv[1] # input filepath as commandline argument
vmLines = clean(filepath) # returns the cleaned up list of lines
boolCounter = 0

outLines = []

# write output lines to new .asm file
outFile = os.path.splitext(filepath)[0]
filename = os.path.basename(outFile)
outFile += ".asm"


# for each line in the cleaned up list of lines
for line in vmLines:
    tempList = line.split() # split the line of text and save into temp list
    argNum = len(tempList)
    if argNum == 1:
        boolCounter, toAppend = oneArgNEW(tempList[0], boolCounter) # run the 1 argument translator function
        for line in toAppend: # append the output to the new outLines
            outLines.append(line)

    # else if the length of the list is 3
    elif argNum == 3:
        toAppend = threeArgNEW(tempList[0], tempList[1], tempList[2], filename)
        for line in toAppend:
            outLines.append(line)
    
    else:
        print("Unable to append, incorrect number of arguments for the command")

# write asm code to outFile
with open(outFile, 'w') as OF:
        for line in outLines:
            OF.write(line + '\n')
