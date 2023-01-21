# this program contains functions for translating vm code to assmebly language.

segmentSymbols = {'local'   : 'LCL', 
                   'this'    : 'THIS',
                   'that'    : 'THAT',
                   'argument': 'ARG'}

segmentConstants = {'pointer' : '3', 
                     'temp'    : '5'}


def oneArgNEW(arg1, boolCounter):
    '''
    Translates vm code with one arugment to assmebly language

        Inputs (String): each argument of the command as a String

        Returns (list of strings): the corresponding code in assmebly language
    '''
    retList = []

    if arg1 not in ["neg", "not"]: # if unarary or jump
        retList.extend(["@SP", "M=M-1", "A=M", "D=M"])

    retList.extend(["@SP", "M=M-1", "@SP", "A=M"]) # decrement stack pointer and
                                                  # set A to stack Pointer

    # add, sub, and, or
    if arg1 == 'add':
        retList.append('M=M+D')
    elif arg1 == 'sub':
        retList.append('M=M-D')
    elif arg1 == 'and':
        retList.append('M=M&D')
    elif arg1 == 'or':
        retList.append('M=M|D')

    # neg, not
    elif arg1 == 'neg':
        retList.append('M=-M')
    elif arg1 == 'not':
        retList.append('M=!M')

    # eq, gt, lt
    elif arg1 in ["eq", "gt", "lt"]:
        retList.append("D=M-D")
        retList.append("@BOOLBEGIN{}".format(boolCounter))

        if arg1 == "eq":
            retList.append("D;JEQ")
        elif arg1 == "gt":
            retList.append("D;JGT")
        elif arg1 == "lt":
            retList.append("D;JLT")

        retList.extend(["@SP", "A=M", "M=0"])
        retList.append("@BOOLEND{}".format(boolCounter))
        retList.append("0;JMP") # set A to stack the stack pointer,
                                # M=0 is false

        retList.append("(BOOLBEGIN{})".format(boolCounter))
        retList.extend(["@SP", "A=M", "M=-1"])
        retList.append("(BOOLEND{})".format(boolCounter))
        boolCounter += 1

    retList.extend(["@SP", "M=M+1"]) # increment the stack pointer

    return boolCounter, retList #return boolCounter as "out parameter to keep track of jumps"

    

def threeArgNEW(arg1, arg2, arg3, filename): # e.g. push constant 5
    '''
    Translates vm code with one arugment to assmebly language

        Inputs (String 1, String 2): each argument of the command as a String

        Returns (list of strings): the corresponding code in assmebly language
    '''
    retList = []
    
    if arg1 == "push":
        if arg2 in segmentSymbols or arg2 in segmentConstants:
            if arg2 in segmentSymbols:
                retList.extend(["@" + segmentSymbols[arg2], "D=M"])
            else:
                retList.extend(["@" + segmentConstants[arg2], "D=A"])
            
            retList.extend(["@" + arg3, "A=D+A", "D=M"])
        elif arg2 == "constant":
            retList.extend(["@" + arg3, "D=A"])
        elif arg2 == "static":
            retList.extend(["@" + filename + "." + arg3, "D=M"])
        
        retList.extend(["@SP", "A=M", "M=D", "@SP", "M=M+1"]) # stack pointer
                                                              # point to top of stack 
    
    
    if arg1 == "pop":
        if arg2 in segmentSymbols or arg2 in segmentConstants:
            if arg2 in segmentSymbols:
                retList.extend(["@" + segmentSymbols[arg2], "D=M"])
            else:
                retList.extend(["@" + segmentConstants[arg2], "D=A"])
            retList.extend(["@" + arg3, "D=D+A"])
        elif arg2 == "static": # can't pop constant, so static only!
            retList.extend(["@" + filename + "." + arg3, "D=A"]) # Xxx.

        retList.extend(["@R13", "M=D", "@SP", "AM=M-1", "D=M", "@R13", "A=M", "M=D"])
    
    return retList