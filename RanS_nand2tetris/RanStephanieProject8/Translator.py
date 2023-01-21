arithmeticSymbols = {
    "add": "M=D+M",
    "sub": "M=M-D",
    "and": "M=D&M",
    "or": "M=D|M",
    "neg": "M=-M",
    "not": "M=!M",
    "eq": "D;JEQ",
    "gt": "D;JGT",
    "lt": "D;JLT",
}

segmentSymbols = {'local'   : 'LCL', 
                   'this'    : 'THIS',
                   'that'    : 'THAT',
                   'argument': 'ARG'}

segmentConstants = {'pointer' : '3', 
                     'temp'    : '5'}


def init(funcLabelCounter):
    '''
    Write the bootstrap vm code
    '''
    out = []
    out.append("// bootstrap init")
    out.append("@256")
    out.append("D=A")
    out.append("@SP")
    out.append("M=D")
    linestoAppend = funcDef("Sys.init", 0)
    for line in linestoAppend:
        out.append(line)
    filler, linestoAppend = funcCall("Sys.init", 0, funcLabelCounter)
    for line in linestoAppend:
        out.append(line)
    
    return out



def label(labelName):
    '''
    Writes a label in assembly code
    '''
    out = []
    out.append("// create label")
    out.append("({})".format(labelName))
    return out

    

def goTo(labelName):
    '''
    Writes a 0;JMP unconditional jump in assembly code
    '''
    out = []
    out.append("// goto")
    out.append("@{}".format(labelName))
    out.append("0;JMP")
    return out


def ifGoTo(labelName):
    '''
    Writes a conditional jump in assembly code
    '''
    out = []
    out.append("// if-go to")
    out.append("@SP")
    out.append("AM=M-1")
    out.append("D=M")
    out.append("@{}".format(labelName))
    out.append("D;JNE")
    return out

def funcDef(funcName, num):
    '''
    Writes function definition
    '''
    out = []
    out.append("// function definition")
    out.append("({})".format(funcName))
    for i in range(int(num)):
        out.append("@SP")
        out.append("A=M")
        out.append("M=0")
        out.append("@SP")
        out.append("M=M+1")
    return out

def funcCall(funcName, num, funcLabelCounter):
    out = []
    retLabel = funcName + "RET" + str(funcLabelCounter)
    print(retLabel)
    funcLabelCounter += 1
    out.append("// function call")
    # push return
    out.append("@" + retLabel)
    out.append("D=A")
    out.append("@SP")
    out.append("A=M")
    out.append("M=D")
    out.append("@SP")
    out.append("M=M+1")

    # push LCL, ARG, THIS, THAT
    for segment in ["LCL", "ARG", "THIS", "THAT"]:
        out.append("@" + segment)
        out.append("D=M")
        out.append("@SP")
        out.append("A=M")
        out.append("M=D")
        out.append("@SP")
        out.append("M=M+1")

    # ARG = SP -n -5 where n is num
    out.append("// done pushing segments, moving on to ARG n-5 stuff")
    out.append("@SP")
    out.append("D=M")
    out.append("@5")
    out.append("D=D-A")
    out.append("@{}".format(num))
    out.append("D=D-A")
    out.append("@ARG")
    out.append("M=D")

    # LCL = SP
    out.append("@SP")
    out.append("D=M")
    out.append("@LCL")
    out.append("M=D")

    # goto f
    out.append("@" + funcName)
    out.append("0;JMP")

    # (return address)
    out.append("(" + retLabel + ")")
    out.append("// done with (return address/all of function call)")

    return funcLabelCounter, out


def funcReturn():
    '''
    Writes function return
    '''
    # FRAME = LCL
    out = []
    out.append("// function return start")
    out.append("@LCL")
    out.append("D=M")
    out.append("@FRAME")
    out.append("M=D")

    # RET = *(FRAME - 5)
    out.append("@FRAME")
    out.append("D=M")
    out.append("@5")
    out.append("A=D-A")
    out.append("D=M")
    out.append("@RET")
    out.append("M=D")

    # ARG = pop()
    out.append("@SP")
    out.append("AM=M-1")
    out.append("D=M")
    out.append("@ARG")
    out.append("A=M")
    out.append("M=D")

    # SP = ARG + 1
    out.append("@ARG")
    out.append("D=M+1")
    out.append("@SP")
    out.append("M=D")

    # THAT = *(FRAME - 1), restore THAT of the caller
    out.append("@FRAME")
    out.append("A=M-1")
    out.append("D=M")
    out.append("@THAT")
    out.append("M=D")

    # THIS = *(FRAME - 2), restore THIS of the caller
    out.append("@FRAME")
    out.append("A=M-1")
    out.append("A=A-1")
    out.append("D=M")
    out.append("@THIS")
    out.append("M=D")

    # ARG = *(FRAME - 3), restore ARG of the caller
    out.append("@FRAME")
    out.append("A=M-1")
    out.append("A=A-1")
    out.append("A=A-1")
    out.append("D=M")
    out.append("@ARG")
    out.append("M=D")

    # LCL = *(FRAME - 4), restore LCL of the caller
    out.append("@FRAME")
    out.append("D=M")
    out.append("@4")
    out.append("A=D-A")
    out.append("D=M")
    out.append("@LCL")
    out.append("M=D")

    # goto RET, go to return address
    out.append("@RET")
    out.append("A=M")
    out.append("0;JMP")
    out.append("// done with function return")

    return out



def arithmetic_command(command):
    '''
    Writes assembly code for add, sub, and, or, neg, not

        Inputs (String): the command as a String

        Returns (list of strings): the translated assembly code as a list of strings
    '''
    out = []
    out.append("// arithmetic commmand begin")
    # if add, sub, and, or
    if command in ["add", "sub", "and", "or"]:
        # Pop SP to D
        popStackToD(out)
        #out.append("A=A-1")
        # Decrement SP
        decSP(out)
        # Append the symbol for the correct arithmentic operator
        out.append(arithmeticSymbols[command])
    # if neg, not
    else:
        #Decrement SP and append command
        decSP(out)
        out.append(arithmeticSymbols[command])
    
    return out


def jump_command(command, labelCounter):
    '''
    Writes assembly code for eq, gt, lt

        Inputs (String): the command as a String

        Returns (list of strings): the translated assembly code as a list of strings
    '''
    out = []
    out.append("// jump command start")
    out.extend(["@SP", "M=M-1", "A=M", "D=M"])
    out.extend(["@SP", "M=M-1", "@SP", "A=M"])
    out.append("D=M-D")
    out.append("@LABELBEGIN{}".format(labelCounter))

    out.append(arithmeticSymbols[command])

    # set false
    out.append("@SP")
    out.append("A=M")
    out.append("M=0")

    # jump label
    out.append("@LABELEND{}".format(labelCounter))

    out.append("0;JMP") # set A to stack the stack pointer,
                                # M=0 is false

    out.append("(LABELBEGIN{})".format(labelCounter))
    out.extend(["@SP", "A=M", "M=-1"])
    out.append("(LABELEND{})".format(labelCounter))


    out.extend(["@SP", "M=M+1"]) # increment the stack pointer
    labelCounter += 1

    return labelCounter, out


def push(arg2, arg3, filename):
    out = []
    out.append("// push start")
    if arg2 in segmentSymbols or arg2 in segmentConstants:
        if arg2 in segmentSymbols:
            out.extend(["@" + segmentSymbols[arg2], "D=M"])
        else:
            out.extend(["@" + segmentConstants[arg2], "D=A"])
            
        
        out.extend(["@" + arg3, "A=D+A", "D=M"])
    elif arg2 == "constant":
        out.extend(["@" + arg3, "D=A"])
    elif arg2 == "static":
        out.extend(["@" + filename + "." + arg3, "D=M"])
    
    out.extend(["@SP", "A=M", "M=D", "@SP", "M=M+1"]) # stack pointer
                                                        # point to top of stack
    
    return out


def pop(arg1, arg2, arg3, filename):
    out = []
    out.append("// pop start")
    if arg2 in segmentSymbols or arg2 in segmentConstants:
        if arg2 in segmentSymbols:
            out.extend(["@" + segmentSymbols[arg2], "D=M"])
        else:
            out.extend(["@" + segmentConstants[arg2], "D=A"])
        out.extend(["@" + arg3, "D=D+A"])
    elif arg2 == "static": # can't pop constant, so static only!
        out.extend(["@" + filename + "." + arg3, "D=A"]) # Xxx.

    out.extend(["@R13", "M=D", "@SP", "AM=M-1", "D=M", "@R13", "A=M", "M=D"])
    
    return out


def popStackToD(out):
    out.append("@SP")
    out.append("AM=M-1")
    out.append("D=M")


def decSP(out):
    out.append("@SP")
    out.append("A=M-1")