import os
import sys

# This program takes a .asm file and outputs a .hack file


keyTracker = 16  # the key tracker starts at 16 since there are already
                 # addresses up to 15 saved

# A symbol table with all the saved RAM address locations
SymbolTable = {
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
    "SCREEN": 16384,
    "KBD": 24576,
    }
    
for i in range(0,16): # adding the registers to the Symbol Table
  key = "R" + str(i)
  SymbolTable[key] = i


# A lookup table with all the computation instructions
comp = {
    "0": "0101010", # when a=0
    "1": "0111111",
    "-1": "0111010",
    "D": "0001100",
    "A": "0110000",
    "!D": "0001101",
    "!A": "0110001",
    "-D": "0001111",
    "-A": "0110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "D+A": "0000010",
    "D-A": "0010011",
    "A-D": "0000111",
    "D&A": "0000000",
    "D|A": "0010101",
    "M": "1110000", # when a=1
    "!M": "1110001",
    "-M": "1110011",
    "M+1": "1110111",
    "M-1": "1110010",
    "D+M": "1000010",
    "D-M": "1010011",
    "M-D": "1000111",
    "D&M": "1000000",
    "D|M": "1010101"
    }


# A lookup table with all the destination instructions
dest = {
    "null": "000",
    "M": "001",
    "D": "010",
    "A": "100",
    "MD": "011",
    "AM": "101",
    "AD": "110",
    "AMD": "111"
    }


# A lookup table with all the jump instructions
jump = {
    "null": "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111"
    }



def addKey(key):
    '''
    Adds a key to the symbol table

        Inputs (string): key; a key to add to the symbol table

        Returns: value of the newly added key
    '''
    
    global keyTracker
    SymbolTable[key] = keyTracker # add the key and memory address pair to the symbol table
    keyTracker += 1 # increment the tracker
    return SymbolTable[key]



def resolveLabels(asmLines):
    '''
    Resolves labels in asm code

        Inputs (list of strings): lines of asm code

        Returns: updated list of lines without labels
    '''
    lineNum = 0
    retLine = []

    for line in asmLines:
        if line[0] == '(':
            key = line[1:-2]
            SymbolTable[key] = lineNum
            line = ''
        else:
            lineNum += 1
            retLine.append(line)

    return retLine



def Ainstruction(line):
    '''
    Performs translation of A instruction to machine code

        Inputs:
            line (string): a line of asm code

        Returns: binary value of the A instruction
    '''
    if (line[1].isalpha()):
        key = line[1:-1]
        decVal = SymbolTable.get(key, -1) # -1 if the key isn't in the table
        if decVal == -1:
            decVal = addKey(key) # saves the value of the key to DecVal
    else:
        decVal = int(line[1:])
    binVal = bin(decVal)[2:].zfill(16)
    return binVal



def Cinstruction(line):
    '''
    Performs translation of C instruction to machine code. First gets each
    component (comp, dest, jump) of the C instruction then combines them to
    get the full instruction

        Inputs:
            line (string): a line of asm code

        Returns: string binary value of the C instruction
    '''

    # initialize values to "null" if 
    line = line[:-1]
    if not "=" in line:
        line = "null=" + line

    if not ";" in line:
        line = line + ";null"
    
    instrList = line.split('=') # splits the instructions up into a list with
                                # [0]dest and [1]comp;jump

    # dest
    destBin = dest.get(instrList[0], "destFail")

    # comp
    instrList = instrList[1].split(';') # splits comp;jump up into a list with
                                        # [0]comp and [1]jump
    compBin = comp.get(instrList[0], "compFail")

    # jump
    jumpBin = jump.get(instrList[1], "jumpFail")
    
    return '111' + compBin + destBin + jumpBin



def clean(filepath):
    '''
    Remove c-style comments and whitespaces from a file

        Inputs:
            filepath (string): the file path

        Returns: nothing (generates out file)
    '''
    newLines=[]
    listofLines = []

    if os.path.exists(filepath):
        with open(filepath, 'r') as f: #open the file for reading
            lines = f.readlines()
            partOfComment=False
            for s in lines:
                if s != "\n": #if the line is not empty
                    k=len(s)
                    if not partOfComment:
                        strLine = ""
                        i=0
                        while i < k:
                            if partOfComment:
                                if(s[i]=="*"):
                                    if(i+1<k and s[i+1]=="/"):
                                        partOfComment=False
                                        i+=1
                                i+=1
                                continue
                            if(s[i]=='\"'):
                                strLine+=s[i]
                                i += 1
                                while i<k and s[i]!='\"':
                                    strLine+=s[i]
                                    i += 1
                                continue

                            #case //
                            if s[i]=='/':
                                if i+1<k and s[i+1]=='/':
                                    strLine+='\n'
                                    break

                                #case /* */
                                if i+1<k and s[i+1]=='*':
                                    partOfComment=True
                                    i+=1

                            if not partOfComment:
                                strLine += s[i]
                            i+=1
                        newLines.append(strLine)

                    else:
                        for i in range(0, k):
                            if s[i]=='*':
                                if i+1<k and s[i+1]=='/':
                                    partOfComment=False
                                    newLines.append("\n")
                
    else:
        raise FileNotFoundError('File does not exist')

    for line in newLines:
        if (line == '\n' or line.isspace()): # if the line is empty or only
                                             # has whitespace
            newLines.remove(line)

    found = False
    for line in newLines:
        if line != '\n' and line != '' and not line.isspace():
            found=True
        if found:
            if line != '\n' and line != '' and not line.isspace():
                line = line.lstrip()
                line = line.rstrip()
                listofLines.append(line + '\n')

    counter = 1
    for line in listofLines:
        counter += 1

    return listofLines



def assemble(asmLines, filepath):
    '''
    Converts the assembly program language to machine language

        Inputs (list): list of assembly language lines

        Returns: nothing. Writes new machine code lines to new .hack file
    '''

    noLabelLines = resolveLabels(asmLines)

    outFile = os.path.splitext(filepath)[0]+'.hack'

    with open(outFile, 'w') as OF:
        for line in noLabelLines:
            if line[0] == '@':
                binLine = Ainstruction(line)
            else:
                binLine = Cinstruction(line)
            OF.write(binLine + '\n')



# script to run the assembler program
filepath = sys.argv[1] # input filepath as commandline argument
asmLines = clean(filepath) # returns the cleaned up list of lines
assemble(asmLines, filepath) # assembles the list of lines and writes to an out
                             # file with .hack extension

