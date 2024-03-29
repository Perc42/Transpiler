import sys
from lexer import *
class Parser:
    def __init__(self, lex, emit):
        self.lex = lex
        self.emit = emit
        self.symbols = set()
        self.labDec = set()
        self.labGoto = set()
        self.curTok = None
        self.peekTok = None
        self.nextTok()
        self.nextTok()
        
    def checkTok(self, kind):
        return kind == self.curTok.kind

    def checkPeek(self, kind):
        return kind == self.peekTok.kind

    def match(self, kind):
        if not self.checkTok(kind):
            self.abort("Expected " + kind.name + ", got " + self.curTok.kind.name)
        self.nextTok()

    def nextTok(self):
        self.curTok = self.peekTok
        self.peekTok = self.lex.getTok()
        
    def CompOp(self):
        return self.checkTok(TokenType.GT) or self.checkTok(TokenType.GTEQ) or self.checkTok(TokenType.LT) or self.checkTok(TokenType.LTEQ) or self.checkTok(TokenType.EQEQ) or self.checkTok(TokenType.NOTEQ)

    def abort(self, message):
        sys.exit("Error! " + message)

    def prog(self):
        self.emit.headerLine("#include <stdio.h>")
        self.emit.headerLine("int main(void){")
        while self.checkTok(TokenType.NEWLINE):
            self.nextTok()
        while not self.checkTok(TokenType.EOF):
            self.statement()
        self.emit.emitLine("return 0;")
        self.emit.emitLine("}")
        for label in self.labGoto:
            if label not in self.labDec:
                self.abort("Attempting to GOTO to undeclared label: " + label)

    def statement(self):
        if self.checkTok(TokenType.PRINT):
            self.nextTok()

            if self.checkTok(TokenType.STRING):
                self.emit.emitLine("printf(\"" + self.curTok.text + "\\n\");")
                self.nextTok()
            else:
                self.emit.emit("printf(\"%" + ".2f\\n\", (float)(")
                self.expres()
                self.emit.emitLine("));")
        elif self.checkTok(TokenType.IF):
            self.nextTok()
            self.emit.emit("if(")
            self.compar()
            self.match(TokenType.THEN)
            self.nl()
            self.emit.emitLine("){")
            while not self.checkTok(TokenType.ENDIF):
                self.statement()
            self.match(TokenType.ENDIF)
            self.emit.emitLine("}")
        elif self.checkTok(TokenType.WHILE):
            self.nextTok()
            self.emit.emit("while(")
            self.compar()
            self.match(TokenType.REPEAT)
            self.nl()
            self.emit.emitLine("){")
            while not self.checkTok(TokenType.ENDWHILE):
                self.statement()
            self.match(TokenType.ENDWHILE)
            self.emit.emitLine("}")
        elif self.checkTok(TokenType.LABEL):
            self.nextTok()
            if self.curTok.text in self.labDec:
                self.abort("Label already exists: " + self.curTok.text)
            self.labDec.add(self.curTok.text)
            self.emit.emitLine(self.curTok.text + ":")
            self.match(TokenType.IDENT)
        elif self.checkTok(TokenType.GOTO):
            self.nextTok()
            self.labGoto.add(self.curTok.text)
            self.emit.emitLine("goto " + self.curTok.text + ";")
            self.match(TokenType.IDENT)
        elif self.checkTok(TokenType.LET):
            self.nextTok()
            if self.curTok.text not in self.symbols:
                self.symbols.add(self.curTok.text)
                self.emit.headerLine("float " + self.curTok.text + ";")
            self.emit.emit(self.curTok.text + " = ")
            self.match(TokenType.IDENT)
            self.match(TokenType.EQ)
            
            self.expres()
            self.emit.emitLine(";")
        elif self.checkTok(TokenType.INPUT):
            self.nextTok()
            if self.curTok.text not in self.symbols:
                self.symbols.add(self.curTok.text)
                self.emit.headerLine("float " + self.curTok.text + ";")
            self.emit.emitLine("if(0 == scanf(\"%" + "f\", &" + self.curTok.text + ")) {")
            self.emit.emitLine(self.curTok.text + " = 0;")
            self.emit.emit("scanf(\"%")
            self.emit.emitLine("*s\");")
            self.emit.emitLine("}")
            self.match(TokenType.IDENT)
        else:
            self.abort("Invalid statement at " + self.curTok.text + " (" + self.curTok.kind.name + ")")
        self.nl()
    def compar(self):
        self.expres()
        if self.CompOp():
            self.emit.emit(self.curTok.text)
            self.nextTok()
            self.expres()
        while self.CompOp():
            self.emit.emit(self.curTok.text)
            self.nextTok()
            self.expres()
            
    def expres(self):
        self.term()
        while self.checkTok(TokenType.PLUS) or self.checkTok(TokenType.MINUS):
            self.emit.emit(self.curTok.text)
            self.nextTok()
            self.term()
    def term(self):
        self.unary()
        while self.checkTok(TokenType.ASTERISK) or self.checkTok(TokenType.SLASH):
            self.emit.emit(self.curTok.text)
            self.nextTok()
            self.unary()
    def unary(self):
        if self.checkTok(TokenType.PLUS) or self.checkTok(TokenType.MINUS):
            self.emit.emit(self.curTok.text)
            self.nextTok()        
        self.prim()
    def prim(self):
        if self.checkTok(TokenType.NUMBER): 
            self.emit.emit(self.curTok.text)
            self.nextTok()
        elif self.checkTok(TokenType.IDENT):
            if self.curTok.text not in self.symbols:
                self.abort("Referencing variable before assignment: " + self.curTok.text)
            self.emit.emit(self.curTok.text)
            self.nextTok()
        else:
            self.abort("Unexpected token at " + self.curTok.text)
    def nl(self):
        self.match(TokenType.NEWLINE)
        while self.checkTok(TokenType.NEWLINE):
            self.nextTok()