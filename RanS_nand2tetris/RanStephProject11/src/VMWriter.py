class VMWriter:
    def __init__(self, output_file):
        self.output = open(output_file, "w")

    # const, arg, LOCAL, STATIC, THIS, THAT, POINTER, TEMP
    def writePush(self, segment, index):
        '''
        Writes a VM push command
        '''
        if segment == 'const':
            segment = 'constant'
        elif segment == 'arg':
            segment = 'argument'
        elif segment == 'var':
            segment = 'local'
        elif segment == 'field':
            segment = 'this'
        
        self.output.write("push {} {}\n".format(segment.lower(), index))

  # const, arg, LOCAL, STATIC, THIS, THAT, POINTER, TEMP
    def writePop(self, segment, index):
        '''
        Writes a VM pop command
        '''
        if segment == 'const':
            segment = 'constant'
        elif segment == 'arg':
            segment = 'argument'
        elif segment == 'var':
            segment = 'local'
        elif segment == 'field':
            segment = 'this'

        self.output.write('pop {} {}\n'.format(segment, index))


  # add, SUB, NEG, EQ, GT, LT, AND, OR, not
    def writeArithmetic(self, command):
        '''
        Writes a VM arithmetic-logical command
        '''
        self.output.write(command.lower() + '\n')


    def writeLabel(self, label):
        '''
        Writes a VM label command
        '''
        self.output.write('label {}'.format(label))


    def writeGoto(self, label):
        '''
        Writes a VM goTO command
        '''
        self.output.write('goto {}'.format(label))


    def writeIf(self, label):
        '''
        Writes a VM if-goto command
        '''
        self.output.write('if-goto {}'.format(label))


    def writeCall(self, name, nArgs):
        '''
        Writes a VM call command
        '''
        self.output.write('call {} {}\n'.format(name, nArgs))


    def writeFunction(self, name, nLocals):
        '''
        Writes a VM function command
        '''
        towrite = "function {} {}\n".format(name, nLocals)
        self.output.write(towrite)


    def writeReturn(self):
        '''
        Writes a VM return command
        '''
        self.output.write('return\n')
    
    def writeSomething(self, something):
        '''
        Writes a VM return command
        '''
        self.output.write(something + "\n")


    def close(self):
        '''
        Closes the output file
        '''
        self.output.close()
        
