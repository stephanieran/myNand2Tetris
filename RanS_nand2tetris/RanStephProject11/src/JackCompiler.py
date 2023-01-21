import sys
import os
import CompilationEngine

# gonna have to change literally all of this
def writeToFile(inFile, outFile):
    '''
    writes tokenizer output to the given output file
    '''
    compEngine = CompilationEngine.CompilationEngine(inFile, outFile)
    compEngine.CompileClass()



#input from tokenizer and writes output using vmWriter
def main():
    # driver code to compile and write to an output .vm file
    inFile = []
    inPath = sys.argv[1]

    if os.path.isfile(inPath) and inPath[-5:] == ".jack": # file
        outFile = inPath[:-5] + ".vm"
        writeToFile(inPath, outFile)

    elif os.path.isdir(inPath): # directory
        if inPath[-1:] == "/":
            inPath = inPath[:-1]
        for file in os.listdir(inPath):
            if file[-5:] == ".jack":
                inFile.append(inPath + "/" + file)
        for file in inFile:
            outFile = file[:-5] + ".vm"
            writeToFile(file, outFile)


if __name__ == '__main__':
    main()