from clean import clean

'''
According to chapter 10 of Nand2Tetris text:
    The JackTokenizer removes all comments and white space from the input
    stream and breaks it into Jack-language tokens, as specified by the
    Jack grammar.
'''

keywordTable = ["class", "method", "function", "constructor", "int", \
					"boolean", "char", "void", "var", "static", "field", \
					"let", "do", "if", "else", "while", "return", "true", \
					"false", "null", "this"]

symbolTable = ['(', ')', '[', ']', '{', '}', ',', ';', '=', '.', '+', '-', '*', \
		 '/', '&', '|', '~', '<', '>']

class JackTokenizer:
    def __init__(self, filepaths):
        self.fileLines = [] # list of strings e.g. ["class Main {", "function void main"]
        cleanedFile = clean(filepaths) # clean the file by removing comments and white spaces
        for line in cleanedFile:
            self.fileLines.append(line)

        self.currToken = ""
        self.currIdx = 0
        self.finalTokenList = []
        self.createTokenList(self.fileLines)
        

    def createTokenList(self, fileLines):
        ''' void function: creates the final list of Tokens after processing'''
        for line in fileLines: # e.g. class Main {
            if any(substr in line for substr in ['\"']): # if the line contains ""
                splitByQuote = line.split('\"') # splits at quotation
                split = splitByQuote[0].split()
                markedStrConst = splitByQuote[1] + "XmarkerX" # marks string constants
                self.appendSplitLine(split)
                self.finalTokenList.append(markedStrConst)
                self.appendSplitLine(splitByQuote[2])
            else:
                split = line.split() # split the line by whitespaces
                self.appendSplitLine(split)
        
        # remove newline characters
        self.finalTokenList = [i for i in self.finalTokenList if i != '\n']
        self.currToken = self.finalTokenList[0]


    def appendSplitLine(self, split):
        '''
        Helper function to create the final token list
        Appends the strings of a line that's been split up
        '''
        for word in split:
            if word.upper() in keywordTable:
                self.finalTokenList.append(word)
            elif word in symbolTable:
                self.finalTokenList.append(word)
            elif word.isdigit():
                self.finalTokenList.append(word)
            else:
                if any(substr in word for substr in symbolTable):
                    self.appendWithSymbol(word)
                else:
                    self.finalTokenList.append(word)


    def appendWithSymbol(self, word):
        '''
        Recursive function that appends strings with symbols.
        '''
        # base case
        if word == "":
            return
        # recursive step
        else:
            if any(char in word for char in symbolTable):
                for char in word:
                    if char in symbolTable:
                        splitWords = word.split(char, 1)
                        if splitWords[0] != "":
                            self.finalTokenList.append(splitWords[0]) # appends first split part ("Output")
                        self.finalTokenList.append(char) #(.)
                        self.appendWithSymbol(splitWords[1])
                        break
            else:
                self.finalTokenList.append(word)
                self.appendWithSymbol("")


    def hasMoreTokens(self):
        '''
        Check if there are more tokens in the input. Returns True/False
        depending on if the file has more tokens
        '''
        if self.currIdx < len(self.finalTokenList)-1:
            return True
        
        return False


    def advance(self):
        '''
        Gets the next token from the input and makes it the current token.
        Should only be called if hasMoreTokens is true.
        '''
        if self.hasMoreTokens():
            self.currToken = self.finalTokenList[self.currIdx + 1] # sets current token to next token
            self.currIdx = self.currIdx + 1
    

    def tokenType(self):
        '''Returns the type of the current token'''
        if self.currToken in keywordTable:
            return "keyword"
        if self.currToken in symbolTable:
            return "symbol"
        if self.currToken.isdigit():
            return "integerConstant"
        if 'XmarkerX' in self.currToken:
            return "stringConstant"
        
        return "identifier"

    def keyword(self):
        '''
        Returns the keyword which is the current token. Called only when
        tokenType is KEYWORD
        '''
        return self.currToken
    

    def symbol(self):
        return self.currToken[0]


    def identifier(self):
        return self.currToken


    def intVal(self):
        return int(self.currToken)


    def stringVal(self):
        return self.currentToken.replace('"', '')
    

    def getToken(self):
        return self.currToken
    

    def peek(self):
        '''
        Returns the next token after the current token
        '''
        nextIdx = self.currIdx + 1
        nextToken = self.finalTokenList[nextIdx]
        return nextToken
    

