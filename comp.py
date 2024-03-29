from lexer import *
from emitter import *
from parser import *
import sys

def main():
    if len(sys.argv) != 2:
        sys.exit("Error: Compiler needs source file as argument.")
    with open(sys.argv[1], 'r') as inputFile:
        source = inputFile.read()
    lexer = Lexer(source)
    emitter = Emitter("out.c")
    parser = Parser(lexer, emitter)
    parser.prog()
    emitter.writeFile()
    print("Compiling completed.")

main()