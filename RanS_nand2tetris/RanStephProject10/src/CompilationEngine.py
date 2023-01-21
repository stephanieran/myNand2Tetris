import JackTokenizer
import sys
import os

'''
According to chapter 10 of Nand2Tetris text:
    The CompilationEngine affects the actual compilation output. It gets its input from a JackTokenizer
    and emits its parsed structure into an output file.
'''

class CompilationEngine:
    def __init__(self, inFile):
        self.tokenizer = JackTokenizer.JackTokenizer(inFile)
        self.outLines = []
        self.tabTracker = 0 # keeps track of indentation to help with debugging


    def CompileClass(self):
        '''
        Compiles a complete class
        '''
        # begin the class compilation
        self.expressionBegin("class")
        self.advanceAndAppend(3)

        # class variable declarations
        if self.tokenizer.keyword() in ["static", "field"]:
            self.CompileClassVarDec()
        
        # subroutine declarations
        while self.tokenizer.keyword() in ["constructor", "function", "method", "void"]:
            self.compileSubroutine()
        
        # end the class compilation
        self.advanceAndAppend(1)
        self.outLines.append("</class>\n")


    def tab(self, indentAmt):
        '''
        Creates indentation to help with debugging
        '''
        tab = ""
        i = 0
        while i < indentAmt:
            tab += "  "
            i += 1
        
        return tab


    def advanceAndAppend(self, steps):
        '''
        Appends the current token and advances to the next token.
        '''
        i = 0
        while i < steps:
            # string constant case
            if self.tokenizer.tokenType() == "stringConstant":
                self.outLines.append(self.tab(self.tabTracker) + "<" + self.tokenizer.tokenType() + "> " + self.tokenizer.currToken[:-8] \
                             + " </" + self.tokenizer.tokenType() + ">\n")
            # <. >, ", & cases
            elif self.tokenizer.currToken == '<':
                self.outLines.append(self.tab(self.tabTracker) + "<" + self.tokenizer.tokenType() + "> " + "&lt;" \
                             + " </" + self.tokenizer.tokenType() + ">\n")
            elif self.tokenizer.currToken == '>':
                self.outLines.append(self.tab(self.tabTracker) + "<" + self.tokenizer.tokenType() + "> " + "&gt;" \
                             + " </" + self.tokenizer.tokenType() + ">\n")
            elif self.tokenizer.currToken == '\"':
                self.outLines.append(self.tab(self.tabTracker) + "<" + self.tokenizer.tokenType() + "> " + "&quot;" \
                             + " </" + self.tokenizer.tokenType() + ">\n")
            elif self.tokenizer.currToken == '&':
                self.outLines.append(self.tab(self.tabTracker) + "<" + self.tokenizer.tokenType() + "> " + "&amp;" \
                             + " </" + self.tokenizer.tokenType() + ">\n")
            # all other cases just append the token itself with its type
            else:
                self.outLines.append(self.tab(self.tabTracker) + "<" + self.tokenizer.tokenType() + "> " + self.tokenizer.currToken \
                             + " </" + self.tokenizer.tokenType() + ">\n")
            self.tokenizer.advance() # move on to the next token
            i += 1


    def CompileClassVarDec(self):
        '''
        Compiles a static declaration or a field declaration
        '''
        while self.tokenizer.keyword() in ["static", "field"]:
            self.expressionBegin("classVarDec")
            self.advanceAndAppend(3)
            while self.tokenizer.getToken() != ';':
                self.advanceAndAppend(1)
            self.advanceAndAppend(1) # appends the ;
            self.expressionEnd("classVarDec")
            

    def compileSubroutine(self):
        '''
        Compiles a complete method, function, or constructor
        '''
        self.expressionBegin("subroutineDec")
        self.advanceAndAppend(4) #e.g. method void dispose (
        self.compileParameterList()
        self.advanceAndAppend(1) # )
        self.expressionBegin("subroutineBody")
        self.advanceAndAppend(1) # {
        if self.tokenizer.getToken() == "var":
            self.compileVarDec()
        if self.tokenizer.getToken() != '}':
            self.compileStatements()
        self.advanceAndAppend(1) # }
        self.expressionEnd("subroutineBody")
        self.expressionEnd("subroutineDec")

    
    def compileParameterList(self):
        '''
        Compiles a (possibly empty) parameter list, not including
        the enclosing "()"
        '''
        self.expressionBegin("parameterList")
        while self.tokenizer.getToken() != ')':
            self.advanceAndAppend(1)
        self.expressionEnd("parameterList")
    

    def compileVarDec(self):
        '''
        Compiles a var declaration
        '''
        while self.tokenizer.getToken() == "var":
            self.expressionBegin("varDec")
            self.advanceAndAppend(3)
            while self.tokenizer.getToken() != ';':
                self.advanceAndAppend(1)
            self.advanceAndAppend(1) # appends the ;
            self.expressionEnd("varDec")


    def compileStatements(self):
        '''
        Compiles a sequence of statements, not including the
        enclosing "{}"; letStatement | ifStatement |
        whileStatement | doStatement | returnStatement
        '''
        self.expressionBegin("statements")
        while self.tokenizer.keyword() in ["let", "if", "while", "do", "return"]:
            if self.tokenizer.keyword() == "let":
                self.compileLet()
            elif self.tokenizer.keyword() == "if":
                self.compileIf()
            elif self.tokenizer.keyword() == "while":
                self.compileWhile()
            elif self.tokenizer.keyword() == "do":
                self.compileDo()
            elif self.tokenizer.keyword() == "return":
                self.compileReturn()
        self.expressionEnd("statements")


    def compileDo(self):
        '''
        Compiles a Do statement
        '''
        self.expressionBegin("doStatement")
        self.advanceAndAppend(2) # do
        if self.tokenizer.getToken() == '(':
            self.advanceAndAppend(1) #(
            self.compileExpressionList()
            self.advanceAndAppend(1) #)# subroutine, method call (has a . in it)
        elif self.tokenizer.getToken() == '.':
            self.advanceAndAppend(3) #. and identifier and (
            self.compileExpressionList()
            self.advanceAndAppend(1) #)
        self.advanceAndAppend(1) # ;
        self.expressionEnd("doStatement")


    def compileLet(self):
        '''
        compiles a Let statement
        '''
        self.expressionBegin("letStatement")
        self.advanceAndAppend(2) # let IDENTIFIER
        if self.tokenizer.getToken() == '[':
            self.advanceAndAppend(1) # [
            self.compileExpression()
            self.advanceAndAppend(1) # ]
        self.advanceAndAppend(1) # =
        self.compileExpression()
        self.advanceAndAppend(1) # ;
        self.expressionEnd("letStatement")


    def compileWhile(self):
        '''
        compiles a While Statement; 'while' '(' expression ')' '{' statements '}'
        '''
        self.expressionBegin("whileStatement")
        self.advanceAndAppend(2) # while (
        self.compileExpression()
        self.advanceAndAppend(2) # ) {
        self.compileStatements()
        self.advanceAndAppend(1) # }
        self.expressionEnd("whileStatement")
    

    def compileReturn(self):
        '''
        compiles a Return statement
        '''
        self.expressionBegin("returnStatement")
        self.advanceAndAppend(1) # return
        if self.tokenizer.getToken() != ';': # this means there's an expression
            self.compileExpression()
        self.advanceAndAppend(1) # ;
        self.expressionEnd("returnStatement")


    def compileIf(self):
        '''
        Compiles an If statement with a possible trailing Else statment
        '''
        self.expressionBegin("ifStatement")
        self.advanceAndAppend(2) # if (
        self.compileExpression()
        self.advanceAndAppend(2) # ) {
        self.compileStatements()
        self.advanceAndAppend(1) # }
        if self.tokenizer.getToken() == "else":
            self.advanceAndAppend(2) # else {
            self.compileStatements()
            self.advanceAndAppend(1) # }
        self.expressionEnd("ifStatement")
    

    def compileExpression(self):
        '''
        Compiles an expression; operators '+'|'-'|'*'|'/'|'&'|'|'|'<'|'>'|'='
        '''
        self.expressionBegin("expression")
        self.compileTerm()
        while self.tokenizer.getToken() in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:
            self.advanceAndAppend(1) #append the operator
            self.compileTerm()

        self.expressionEnd("expression")
    

    def compileTerm(self):
        '''
        Compiles a term. This routine is faced with a slight difficulty
        when trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routine must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of “[“, “(“, or “.”
        suffices to distinguish between the three possibilities. Any other token
        is not part of this term and should not be advanced over.

        integerConstant | stringConstant | keywordConstant | varName | varName
        '[' expression ']' | subroutineCall | '(' expression ')' | unaryOp term

        '''
        self.expressionBegin("term")
        if self.tokenizer.tokenType() in ["integerConstant", "stringConstant", "keyword"]: #integer constant
            self.advanceAndAppend(1)
        elif self.tokenizer.tokenType() == "identifier":
            self.advanceAndAppend(1) #append <identifier> x </identifier>
            # array
            if self.tokenizer.getToken() == '[':
                self.advanceAndAppend(1) #[
                self.compileExpression()
                self.advanceAndAppend(1) #]
            # subroutine call
            elif self.tokenizer.getToken() == '(':
                self.advanceAndAppend(1) #(
                self.compileExpressionList()
                self.advanceAndAppend(1) #)
            # subroutine, method call (has a . in it)
            elif self.tokenizer.getToken() == '.':
                self.advanceAndAppend(3) #. and identifier and ()
                self.compileExpressionList()
                self.advanceAndAppend(1) #)
        elif self.tokenizer.tokenType() == "symbol":
            if self.tokenizer.getToken() == '(':
                self.advanceAndAppend(1) #(
                self.compileExpression()
                self.advanceAndAppend(1) #)
            elif self.tokenizer.getToken() in ['-', '~']:
                self.advanceAndAppend(1) # ~
                self.compileTerm()

        self.expressionEnd("term")
    

    def compileExpressionList(self):
        '''
        Compiles a (possibly empty) comma- separated list of expressions.
        '''
        self.expressionBegin("expressionList")
        while self.tokenizer.getToken() != ')':
            self.compileExpression()
            if self.tokenizer.getToken() == ',':
                self.advanceAndAppend(1)
        self.expressionEnd("expressionList")

    
    def expressionBegin(self, str):
        '''
        Writes the beginning of an expression
        '''
        self.outLines.append(self.tab(self.tabTracker) + "<" + str + ">\n")
        self.tabTracker += 1


    def expressionEnd(self, str):
        '''
        Writes the ending of an expression
        '''
        self.tabTracker -= 1
        self.outLines.append(self.tab(self.tabTracker) + "</" + str + ">\n")



def writeToFile(inFile, outFile):
    '''
    writes tokenizer output to the given output file
    '''
    compEngine = CompilationEngine(inFile)
    compEngine.CompileClass()
    
    with open(outFile, 'w') as OF:
        for line in compEngine.outLines:
            OF.write(line)
    

def main():
    # driver code to compile and write to an output .xml file
    inFile = []
    inPath = sys.argv[1]

    if os.path.isfile(inPath) and inPath[-5:] == ".jack": # file
        outFile = inPath[:-5] + ".xml"
        writeToFile(inPath, outFile)
    elif os.path.isdir(inPath): # directory
        if inPath[-1:] == "/":
            inPath = inPath[:-1]
        for file in os.listdir(inPath):
            if file[-5:] == ".jack":
                inFile.append(inPath + "/" + file)
        for file in inFile:
            outFile = file[:-5] + ".xml"
            writeToFile(file, outFile)


if __name__ == '__main__':
    main()