import JackTokenizer
import SymbolTable
import VMWriter
import sys
import os

'''
According to chapter 10 of Nand2Tetris text:
    The CompilationEngine affects the actual compilation output. It gets its input from a JackTokenizer
    and emits its parsed structure into an output file.
'''

class CompilationEngine:
    arithmeticOperators = {
        '+': 'ADD',
        '-': 'SUB',
        '=': 'EQ',
        '>': 'GT',
        '<': 'LT',
        '&': 'AND',
        '|': 'OR'
    }

    unaryArithmeticOperators = {
        '-': 'NEG',
        '~': 'NOT'
    }

    def __init__(self, inFile, outFile):
        self.tokenizer = JackTokenizer.JackTokenizer(inFile)
        self.vmWriter = VMWriter.VMWriter(outFile)
        self.outLines = []
        self.tabTracker = 0 # keeps track of indentation to help with debugging
        self.symbolTable = SymbolTable.SymbolTable()
        self.className = ""
        self.whileIdx = -1 # -1 so that the first label is idx 0
        self.ifIdx = -1
        self.subKind = "" # kind of subroutine call (e.g. method, constructor, function)


    def CompileClass(self):
        '''
        Compiles a complete class
        '''
        # begin the class compilation
        self.expressionBegin("class")
        self.advanceAndAppend(1) # class
        self.className = self.tokenizer.getToken() # className
        self.advanceAndAppend(1) # className
        self.advanceAndAppend(1) # {

        # class variable declarations
        while self.tokenizer.keyword() in ["static", "field"]:
            self.CompileClassVarDec()
        
        # subroutine declarations
        while self.tokenizer.keyword() in ["constructor", "function", "method", "void"]:
            self.compileSubroutine()
        
        # end the class compilation
        self.advanceAndAppend(1)
        self.outLines.append("</class>\n")

        self.vmWriter.close()


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
        self.expressionBegin("classVarDec")
        kind = self.tokenizer.getToken() # ('static' | 'field' )
        self.advanceAndAppend(1)
        type = self.tokenizer.getToken() # type
        self.advanceAndAppend(1)
        name = self.tokenizer.getToken() # varName
        self.advanceAndAppend(1)
        self.symbolTable.define(name, type, kind) # ADD TO SYMBOL TABLE
        while self.tokenizer.getToken() != ';':
            self.advanceAndAppend(1) # ,
            name = self.tokenizer.getToken() # varName
            self.advanceAndAppend(1) # appends varName
            self.symbolTable.define(name, type, kind) # ADD TO SYMBOL TABLE
        self.advanceAndAppend(1) # appends the ;
        self.expressionEnd("classVarDec")
        

    def compileSubroutine(self):
        '''
        Compiles a complete method, function, or constructor
        '''
        varCounts = 0
        self.expressionBegin("subroutineDec")
        self.symbolTable.startSubroutine(self.className)
        
        self.subKind = self.tokenizer.getToken() # e.g. method

        self.advanceAndAppend(2) #e.g. method void
        subroutineName = self.tokenizer.getToken()
        functionName = '{}.{}'.format(self.className, subroutineName)
        self.advanceAndAppend(1) #dispose
        self.advanceAndAppend(1) #(

        self.compileParameterList()
        self.advanceAndAppend(1) # )
        self.expressionBegin("subroutineBody")
        self.advanceAndAppend(1) # {
        if self.tokenizer.getToken() == "var":
            self.compileVarDec()
            varCounts = self.symbolTable.varCount("var")
        self.vmWriter.writeFunction(functionName, varCounts)
        #if method
        if self.subKind == "method":
            self.vmWriter.writePush("arg", 0)
            self.vmWriter.writePop("pointer", 0)
        # if constructor
        if self.subKind == "constructor":
            fieldCount = self.symbolTable.varCount("field")
            self.vmWriter.writePush("const", fieldCount)
            self.vmWriter.writeCall("Memory.alloc", 1)
            self.vmWriter.writePop("pointer", 0)
        
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
            type = self.tokenizer.getToken() # e.g. int
            self.advanceAndAppend(1)

            name = self.tokenizer.getToken() # e.g. Ax (varName)
            self.advanceAndAppend(1)

            self.symbolTable.define(name, type, 'arg')
            if self.tokenizer.getToken() == ',':
                self.advanceAndAppend(1) # appends ,

        self.expressionEnd("parameterList")
    

    def compileVarDec(self):
        '''
        Compiles a var declaration
        '''
        while self.tokenizer.getToken() == "var":
            self.expressionBegin("varDec")
            
            self.advanceAndAppend(1) # appends var

            type = self.tokenizer.getToken() # int
            self.advanceAndAppend(1) # appends int

            name = self.tokenizer.getToken() # varName
            self.advanceAndAppend(1)
            self.symbolTable.define(name, type, 'var')

            while self.tokenizer.getToken() != ';':
                type = self.tokenizer.getToken()
                self.advanceAndAppend(1) # appends ,

                name = self.tokenizer.getToken()
                self.advanceAndAppend(1) # appends varName
                self.symbolTable.define(name, type, 'var')

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
        self.advanceAndAppend(1) # do
        name1 = self.tokenizer.getToken()
        numArgs = 1
        if self.subKind == "constructor":
            numArgs = 0
        self.advanceAndAppend(1) # Name
        if self.tokenizer.getToken() == '(':
            # e.g. draw(), implied that it's a method
            numArgs = 1
            temp = "{}.{}".format(self.className, name1)
            name1 = temp
            self.advanceAndAppend(1) #(
            numArgs += self.compileExpressionList()
            self.vmWriter.writePush("pointer", 0)
            self.vmWriter.writeCall(name1, numArgs)
            self.advanceAndAppend(1) #)# subroutine, method call (has a . in it)
        elif self.tokenizer.getToken() == '.':
            self.advanceAndAppend(1) #.
            if name1 in self.symbolTable.subroutine_scope:
                temp = self.symbolTable.subroutine_scope[name1][0]
                name1 = temp
                self.vmWriter.writePush("local", 0) # self/the class
            if name1 in self.symbolTable.field_scope:
                temp = self.symbolTable.field_scope[name1][0]
                name1 = temp
                self.vmWriter.writePush("this", 0)
            name2 = self.tokenizer.getToken()
            funcName = "{}.{}".format(name1, name2)
            self.advanceAndAppend(1) # identifier 
            self.advanceAndAppend(1) # #(
            numArgs += self.compileExpressionList()
            if name1 in self.symbolTable.field_scope:
                self.vmWriter.writePush("this", 0)
            self.vmWriter.writeCall(funcName, numArgs)
            self.advanceAndAppend(1) #)
        self.advanceAndAppend(1) # ;
        self.vmWriter.writePop("temp", 0)
        self.expressionEnd("doStatement")


    def compileLet(self):
        '''
        compiles a Let statement
        '''
        self.expressionBegin("letStatement")
        self.advanceAndAppend(1) # let
        name = self.tokenizer.getToken()
        kind = self.symbolTable.kindOf(name)
        
        idx = self.symbolTable.indexOf(name)

        self.advanceAndAppend(1) #IDENTIFIER
        # if array
        if self.tokenizer.getToken() == '[':
            self.advanceAndAppend(1) # [
            self.compileExpression()
            self.advanceAndAppend(1) # ]
            self.advanceAndAppend(1) # =
            self.vmWriter.writePush(kind, idx)
            self.vmWriter.writeArithmetic("add")
            self.compileExpression()
            self.advanceAndAppend(1) # ;
            self.vmWriter.writePop("temp", 0)
            self.vmWriter.writePop("pointer", 1)
            self.vmWriter.writePush("temp", 0)
            self.vmWriter.writePop("that", 0)
        else:
            self.advanceAndAppend(1) # =
            self.compileExpression()
            self.advanceAndAppend(1) # ;
            self.vmWriter.writePop(kind, idx) #if issue w xml check here

        self.expressionEnd("letStatement")


    def compileWhile(self):
        '''
        compiles a While Statement; 'while' '(' expression ')' '{' statements '}'
        '''
        self.whileIdx += 1
        idx = self.whileIdx
        self.vmWriter.writeLabel('WHILE{}\n'.format(idx))
        self.expressionBegin("whileStatement")
        self.advanceAndAppend(2) # while (
        self.compileExpression()
        self.advanceAndAppend(2) # ) {
        self.vmWriter.writeArithmetic("not")
        self.vmWriter.writeIf('WHILE_END{}\n'.format(idx))
        self.compileStatements()
        self.vmWriter.writeGoto('WHILE{}\n'.format(idx))
        self.vmWriter.writeLabel('WHILE_END{}\n'.format(idx))
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
        else:
            self.vmWriter.writePush("const", 0)
        self.vmWriter.writeReturn()
        self.advanceAndAppend(1) # ;
        self.expressionEnd("returnStatement")


    def compileIf(self):
        '''
        Compiles an If statement with a possible trailing Else statment
        '''
        self.ifIdx += 1
        idx = self.ifIdx
        
        self.expressionBegin("ifStatement")
        self.advanceAndAppend(2) # if (
        self.compileExpression()
        self.advanceAndAppend(2) # ) {
        self.vmWriter.writeIf('IF_TRUE{}\n'.format(idx))
        self.vmWriter.writeGoto('IF_FALSE{}\n'.format(idx))
        self.vmWriter.writeLabel('IF_TRUE{}\n'.format(idx))
        self.compileStatements()
        self.vmWriter.writeGoto('IF_END{}\n'.format(idx))
        self.advanceAndAppend(1) # }
        self.vmWriter.writeLabel('IF_FALSE{}\n'.format(idx))

        if self.tokenizer.getToken() == "else":
            self.advanceAndAppend(2) # else {
            self.compileStatements()
            self.advanceAndAppend(1) # }
        
        self.vmWriter.writeLabel('IF_END{}\n'.format(idx))
        self.expressionEnd("ifStatement")
    

    def compileExpression(self):
        '''
        Compiles an expression; operators '+'|'-'|'*'|'/'|'&'|'|'|'<'|'>'|'='
        '''
        self.expressionBegin("expression")
        self.compileTerm()
        while self.tokenizer.getToken() in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:
            operator = self.tokenizer.getToken()
            self.advanceAndAppend(1) #append the operator
            self.compileTerm()

            if operator in self.arithmeticOperators.keys():
                self.vmWriter.writeArithmetic(self.arithmeticOperators[operator])
            elif operator == '*':
                self.vmWriter.writeCall('Math.multiply', 2)
            elif operator == '/':
                self.vmWriter.writeCall('Math.divide', 2)
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
        name1 = self.tokenizer.getToken()
        numArgs = 1

        if self.tokenizer.tokenType() in ["integerConstant", "stringConstant", "keyword"]: #integer constant
            if self.tokenizer.tokenType() == "integerConstant":
                self.vmWriter.writePush("const", self.tokenizer.getToken()) #may causes issue
            elif self.tokenizer.tokenType() == "keyword":
                kw = self.tokenizer.getToken()
                if kw == "this":
                    self.vmWriter.writePush("pointer", 0)
                else:
                    self.vmWriter.writePush("constant", 0)
                    if kw == "true":
                        self.vmWriter.writeArithmetic("not")
            elif self.tokenizer.tokenType() == "stringConstant":
                self.compileString()
            self.advanceAndAppend(1)
        elif self.tokenizer.tokenType() == "identifier":
            varKind = self.symbolTable.kindOf(self.tokenizer.getToken())
            varIdx = self.symbolTable.indexOf(self.tokenizer.getToken())
            arrName = self.tokenizer.getToken()
            self.advanceAndAppend(1) #append <identifier> x </identifier>
            # array
            if self.tokenizer.getToken() == '[':
                
                self.advanceAndAppend(1) #[
                self.compileExpression()
                self.advanceAndAppend(1) #]

                arrKind = self.symbolTable.kindOf(arrName)
                arrIdx = self.symbolTable.indexOf(arrName)

                self.vmWriter.writePush(arrKind, arrIdx)
                self.vmWriter.writeArithmetic("add")
                self.vmWriter.writePop("pointer", 1)
                self.vmWriter.writePush("that", 0)
            # subroutine call
            elif self.tokenizer.getToken() == '(':
                self.advanceAndAppend(1) #(
                self.compileExpressionList()
                self.advanceAndAppend(1) #)
            # subroutine, method call (has a . in it)
            elif self.tokenizer.getToken() == '.':
                self.advanceAndAppend(1) #.
                name2 = self.tokenizer.getToken()
                self.advanceAndAppend(1) # identifier
                self.advanceAndAppend(1) # (
                if name1 == "Main":
                    numArgs = 0
                if name1 != self.className:
                    numArgs = 0
                if self.subKind == "function":
                    numArgs = 1

                for x in self.symbolTable.field_scope:
                    if name1 == self.symbolTable.field_scope[x][0]:
                        numArgs = 1

                numArgs += self.compileExpressionList()
                funcName = "{}.{}".format(name1, name2)
                self.vmWriter.writeCall(funcName, numArgs)
                self.advanceAndAppend(1) #)
            else:
                self.vmWriter.writePush(varKind, varIdx)
        elif self.tokenizer.tokenType() == "symbol":
            if self.tokenizer.getToken() == '(':
                self.advanceAndAppend(1) #(
                self.compileExpression()
                self.advanceAndAppend(1) #)
            elif self.tokenizer.getToken() in ['-', '~']:
                operator = self.tokenizer.getToken()
                self.advanceAndAppend(1) # ~
                self.compileTerm()
                self.vmWriter.writeArithmetic(self.unaryArithmeticOperators[operator])

        self.expressionEnd("term")
    
    def compileString(self):
        '''
        compiles a string constant
        '''
        string = self.tokenizer.getToken()
        self.vmWriter.writePush("constant", len(string) - 8)
        self.vmWriter.writeCall('String.new', 1)
        for char in string[:-8]:
            self.vmWriter.writePush('constant', ord(char))
            self.vmWriter.writeCall('String.appendChar', 2)


    def compileExpressionList(self):
        '''
        Compiles a (possibly empty) comma- separated list of expressions.
        '''
        numArgs = 0
        
        self.expressionBegin("expressionList")
        while self.tokenizer.getToken() != ')':
            self.compileExpression()
            if self.tokenizer.getToken() == ',':
                self.advanceAndAppend(1)
                numArgs += 1
        self.expressionEnd("expressionList")
        return numArgs

    
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
