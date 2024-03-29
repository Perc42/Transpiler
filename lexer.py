import sys
import enum

class Lexer:
    def __init__(self, source):
        self.source = source + '\n'
        self.curCh = ''
        self.curpos = -1
        self.nextCh()

    def nextCh(self):
        self.curpos += 1
        if self.curpos >= len(self.source):
            self.curCh = '\0'  # EOF
        else:
            self.curCh = self.source[self.curpos]
    def peek(self):
        if self.curpos + 1 >= len(self.source):
            return '\0'
        return self.source[self.curpos+1]

    def abort(self, message):
        sys.exit("Lexing error. " + message)
    def getTok(self):
        self.skipWhite()
        self.skipComm()
        token = None

        if self.curCh == '+':
            token = Token(self.curCh, TokenType.PLUS)
        elif self.curCh == '-':
            token = Token(self.curCh, TokenType.MINUS)
        elif self.curCh == '*':
            token = Token(self.curCh, TokenType.ASTERISK)
        elif self.curCh == '/':
            token = Token(self.curCh, TokenType.SLASH)
        elif self.curCh == '=':
            if self.peek() == '=':
                lastChar = self.curCh
                self.nextCh()
                token = Token(lastChar + self.curCh, TokenType.EQEQ)
            else:
                token = Token(self.curCh, TokenType.EQ)
        elif self.curCh == '>':
            if self.peek() == '=':
                lastChar = self.curCh
                self.nextCh()
                token = Token(lastChar + self.curCh, TokenType.GTEQ)
            else:
                token = Token(self.curCh, TokenType.GT)
        elif self.curCh == '<':
            if self.peek() == '=':
                lastChar = self.curCh
                self.nextCh()
                token = Token(lastChar + self.curCh, TokenType.LTEQ)
            else:
                token = Token(self.curCh, TokenType.LT)
        elif self.curCh == '!':
            if self.peek() == '=':
                lastChar = self.curCh
                self.nextCh()
                token = Token(lastChar + self.curCh, TokenType.NOTEQ)
            else:
                self.abort("Expected !=, got !" + self.peek())

        elif self.curCh == '\"':
            self.nextCh()
            startPos = self.curpos

            while self.curCh != '\"':
                if self.curCh == '\r' or self.curCh == '\n' or self.curCh == '\t' or self.curCh == '\\' or self.curCh == '%':
                    self.abort("Illegal character in string.")
                self.nextCh()

            tokText = self.source[startPos : self.curpos]
            token = Token(tokText, TokenType.STRING)

        elif self.curCh.isdigit():
            startPos = self.curpos
            while self.peek().isdigit():
                self.nextCh()
            if self.peek() == '.':
                self.nextCh()
                if not self.peek().isdigit(): 
                    self.abort("Illegal character in number.")
                while self.peek().isdigit():
                    self.nextCh()

            tokText = self.source[startPos : self.curpos + 1]
            token = Token(tokText, TokenType.NUMBER)
        elif self.curCh.isalpha():
            startPos = self.curpos
            while self.peek().isalnum():
                self.nextCh()
            tokText = self.source[startPos : self.curpos + 1]
            keyword = Token.checkIfKeyword(tokText)
            if keyword == None:
                token = Token(tokText, TokenType.IDENT)
            else:
                token = Token(tokText, keyword)
        elif self.curCh == '\n':
            token = Token('\n', TokenType.NEWLINE)
        elif self.curCh == '\0':
            token = Token('', TokenType.EOF)
        else:
            self.abort("Unknown token: " + self.curCh)
        self.nextCh()
        return token
    def skipWhite(self):
        while self.curCh == ' ' or self.curCh == '\t' or self.curCh == '\r':
            self.nextCh()

    def skipComm(self):
        if self.curCh == '#':
            while self.curCh != '\n':
                self.nextCh()

class Token:   
    def __init__(self, tokenText, tokenKind):
        self.text = tokenText
        self.kind = tokenKind

    @staticmethod
    def checkIfKeyword(tokenText):
        for kind in TokenType:
            if kind.name == tokenText and kind.value >= 100 and kind.value < 200:
                return kind
        return None

class TokenType(enum.Enum):
    EOF = -1
    NEWLINE = 0
    NUMBER = 1
    IDENT = 2
    STRING = 3
    LABEL = 101
    GOTO = 102
    PRINT = 103
    INPUT = 104
    LET = 105
    IF = 106
    THEN = 107
    ENDIF = 108
    WHILE = 109
    REPEAT = 110
    ENDWHILE = 111
    EQ = 201  
    PLUS = 202
    MINUS = 203
    ASTERISK = 204
    SLASH = 205
    EQEQ = 206
    NOTEQ = 207
    LT = 208
    LTEQ = 209
    GT = 210
    GTEQ = 211