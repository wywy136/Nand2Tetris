from typing import List
from references import Expressions


class Parser:
    def __init__(self):
        self.tokenized = None
        # pointer to a line of tokenization
        self.pointer = 0
        self.indentation = '\t'
        # result XML
        self.xml = []
        # number of indentation currently
        self.idNum = 0
        self.subroutineKW = ['constructor', 'function', 'method']
        self.kwToStatement = {
            'let': self.compileLetStatement,
            'if': self.compileIfStatement,
            'while': self.compileWhileStatement,
            'do': self.compileDoStatement,
            'return': self.compileReturnStatement
        }

    def clearState(self):
        self.tokenized = None
        self.pointer = 0
        self.xml = []
        self.idNum = 0

    # get jack code for a line of tokenization
    def getCode(self, line: str):
        return line.split(' ')[1]

    def getType(self, line: str):
        return line.split(' ')[0][1:-1]

    def write(self, line):
        self.xml.append(self.indentation * self.idNum + line + '\n')

    def pointerIncrement(self):
        self.pointer += 1

    def writeContinuous(self, span, idNum):
        for i in range(span):
            self.write(self.indentation * idNum + self.tokenized[self.pointer])
            self.pointerIncrement()

    def compileClass(self):
        self.write('<class>')
        # 'class', classname, '{'
        self.idNum += 1
        for i in range(3):
            self.write(self.tokenized[self.pointer])
            self.pointerIncrement()
        # classVarDec*
        self.compileClassVarDec()
        # subroutineDec*
        self.compileSubroutineDec()
        # '}'
        self.write(self.tokenized[self.pointer])
        self.pointerIncrement()
        self.idNum -= 1
        self.write('</class>')

    def compileClassVarDec(self):
        # No variables
        if self.getCode(self.tokenized[self.pointer]) in self.subroutineKW:
            return

        # One or more variables
        while self.getCode(self.tokenized[self.pointer]) not in self.subroutineKW:
            self.write('<classVarDec>')
            self.idNum += 1
            # ('static' | 'field'), 'type', 'varname', (',', 'varname')*
            while self.getCode(self.tokenized[self.pointer]) != ';':
                self.write(self.tokenized[self.pointer])
                self.pointerIncrement()
            # ';'
            self.write(self.tokenized[self.pointer])
            self.pointerIncrement()
            self.idNum -= 1
            self.write('</classVarDec>')

    def compileSubroutineDec(self):
        # No routines
        if self.getCode(self.tokenized[self.pointer]) not in self.subroutineKW:
            return

        # one or more routines
        while self.getCode(self.tokenized[self.pointer]) in self.subroutineKW:
            self.write('<subroutineDec>')
            self.idNum += 1
            # ('constructor'|'function'|'method'), ('void'|type), subroutineName, '('
            for i in range(4):
                self.write(self.tokenized[self.pointer])
                self.pointerIncrement()
            # parameterList
            self.compileParameterList()
            # ')'
            self.write(self.tokenized[self.pointer])
            self.pointerIncrement()
            # subroutineBody
            self.compileSubroutineBody()

            self.idNum -= 1
            self.write('</subroutineDec>')

    def compileSubroutineBody(self):
        self.write('<subroutineBody>')
        self.idNum += 1
        # '{'
        self.write(self.tokenized[self.pointer])
        self.pointerIncrement()
        # verDec*
        self.compileVarDec()
        # statement*
        self.compileStatements()
        # '}'
        self.write(self.tokenized[self.pointer])
        self.pointerIncrement()
        self.idNum -= 1
        self.write('</subroutineBody>')

    def compileStatements(self):
        self.write('<statements>')
        self.idNum += 1

        # one or more statements
        while self.getCode(self.tokenized[self.pointer]) != '}':
            # let|if|while|do|return
            try:
                self.kwToStatement[self.getCode(self.tokenized[self.pointer])]()
            except:
                print(self.pointer)

        self.idNum -= 1
        self.write('</statements>')

    def compileLetStatement(self):
        self.write('<letStatement>')
        self.idNum += 1

        # 'let', 'varname'
        for i in range(2):
            self.write(self.tokenized[self.pointer])
            self.pointerIncrement()
        # ('[', expression, ']')?
        if self.getCode(self.tokenized[self.pointer]) == '[':
            # '['
            self.write(self.tokenized[self.pointer])
            self.pointerIncrement()
            # expression
            self.compileExpression()
            # ']'
            self.write(self.tokenized[self.pointer])
            self.pointerIncrement()

        # '='
        self.write(self.tokenized[self.pointer])
        self.pointerIncrement()
        # expression
        self.compileExpression()
        # ';'
        self.write(self.tokenized[self.pointer])
        self.pointerIncrement()

        self.idNum -= 1
        self.write('</letStatement>')

    def compileIfStatement(self):
        self.write('<ifStatement>')
        self.idNum += 1
        # 'if', '('
        for i in range(2):
            self.write(self.tokenized[self.pointer])
            self.pointerIncrement()
        # expression
        self.compileExpression()
        # ')', '{'
        for i in range(2):
            self.write(self.tokenized[self.pointer])
            self.pointerIncrement()
        # statements
        self.compileStatements()
        # '}'
        self.write(self.tokenized[self.pointer])
        self.pointerIncrement()
        # ('else', '{', statements, '}')?
        if self.getCode(self.tokenized[self.pointer]) == 'else':
            # 'else', '{'
            for i in range(2):
                self.write(self.tokenized[self.pointer])
                self.pointerIncrement()
            # statements
            self.compileStatements()
            # '}'
            self.write(self.tokenized[self.pointer])
            self.pointerIncrement()

        self.idNum -= 1
        self.write('</ifStatement>')

    def compileWhileStatement(self):
        self.write('<whileStatement>')
        self.idNum += 1
        # 'while', '('
        for i in range(2):
            self.write(self.tokenized[self.pointer])
            self.pointerIncrement()
        # expression
        self.compileExpression()
        # ')', '{'
        for i in range(2):
            self.write(self.tokenized[self.pointer])
            self.pointerIncrement()
        # statements
        self.compileStatements()
        # '}'
        self.write(self.tokenized[self.pointer])
        self.pointerIncrement()

        self.idNum -= 1
        self.write('</whileStatement>')

    def compileDoStatement(self):
        self.write('<doStatement>')
        self.idNum += 1
        # 'do'
        self.write(self.tokenized[self.pointer])
        self.pointerIncrement()
        # subroutineCall
        self.compileSubroutineCall()
        # ';'
        self.write(self.tokenized[self.pointer])
        self.pointerIncrement()
        self.idNum -= 1
        self.write('</doStatement>')

    def compileReturnStatement(self):
        self.write('<returnStatement>')
        self.idNum += 1
        # 'return'
        self.write(self.tokenized[self.pointer])
        self.pointerIncrement()
        # expression
        if self.getCode(self.tokenized[self.pointer]) != ';':
            self.compileExpression()
        # ';'
        self.write(self.tokenized[self.pointer])
        self.pointerIncrement()
        self.idNum -= 1
        self.write('</returnStatement>')

    def compileExpression(self):
        self.write('<expression>')
        self.idNum += 1

        # term
        self.compileTerm()
        # (op term)*
        if self.getCode(self.tokenized[self.pointer]) in Expressions.op:
            # op
            self.write(self.tokenized[self.pointer])
            self.pointerIncrement()
            # term
            self.compileTerm()

        self.idNum -= 1
        self.write('</expression>')

    def compileTerm(self):
        self.write('<term>')
        self.idNum += 1
        # case: interger constant | string constant | kw constant
        try:
            # case: unaryOp, term
            if self.getCode(self.tokenized[self.pointer]) in Expressions.unaryOp:
                # unaryOp
                self.write(self.tokenized[self.pointer])
                self.pointerIncrement()
                # term
                self.compileTerm()
            elif (self.getType(self.tokenized[self.pointer]) in ['integerConstant', 'stringConstant']) or \
                    (self.getCode(self.tokenized[self.pointer]) in Expressions.kwConstant):
                self.write(self.tokenized[self.pointer])
                self.pointerIncrement()
            # case: subroutineCall
            elif (self.getCode(self.tokenized[self.pointer]) != '(') and \
                    (self.getCode(self.tokenized[self.pointer + 1])) in ['(', '.']:
                self.compileSubroutineCall()
            # case: '(', expression, ')'
            elif self.getCode(self.tokenized[self.pointer]) == '(':
                # '('
                self.write(self.tokenized[self.pointer])
                self.pointerIncrement()
                # expression
                self.compileExpression()
                # ')'
                self.write(self.tokenized[self.pointer])
                self.pointerIncrement()

            # case: varName | varName, '[', expression, ']'
            else:
                # varName
                self.write(self.tokenized[self.pointer])
                self.pointerIncrement()
                if self.getCode(self.tokenized[self.pointer]) == '[':
                    # '['
                    self.write(self.tokenized[self.pointer])
                    self.pointerIncrement()
                    # expression
                    self.compileExpression()
                    # ']'
                    self.write(self.tokenized[self.pointer])
                    self.pointerIncrement()
        except:
            print(len(self.tokenized), self.pointer)

        self.idNum -= 1
        self.write('</term>')

    def compileSubroutineCall(self):
        # case： (className | varName), '.', subroutineName, '(', expressionList, ')'
        if self.getCode(self.tokenized[self.pointer + 1]) == '.':
            # (className | varName), '.', subroutineName, '('
            for i in range(4):
                self.write(self.tokenized[self.pointer])
                self.pointerIncrement()
        # case: subroutineName, '(', expressionList, ')'
        else:
            for i in range(2):
                self.write(self.tokenized[self.pointer])
                self.pointerIncrement()
        # expressionList
        self.compileExpressionList()
        # ')'
        self.write(self.tokenized[self.pointer])
        self.pointerIncrement()

    def compileExpressionList(self):
        self.write('<expressionList>')
        self.idNum += 1
        # no expression
        if self.getCode(self.tokenized[self.pointer]) == ')':
            self.idNum -= 1
            self.write('</expressionList>')
            return
        # expression
        self.compileExpression()
        # (',', expression)*
        while self.getCode(self.tokenized[self.pointer]) != ')':
            # ','
            self.write(self.tokenized[self.pointer])
            self.pointerIncrement()
            # expression
            self.compileExpression()
        self.idNum -= 1
        self.write('</expressionList>')

    def compileParameterList(self):
        self.write('<parameterList>')
        self.idNum += 1
        # not reach the end of the list
        while self.getCode(self.tokenized[self.pointer]) != ')':
            self.write(self.tokenized[self.pointer])
            self.pointerIncrement()
        self.idNum -= 1
        self.write('</parameterList>')

    def compileVarDec(self):
        # one or more lines or varDec
        while self.getCode(self.tokenized[self.pointer]) == 'var':
            self.write('<varDec>')
            self.idNum += 1
            # 'var', typename, varname
            for i in range(3):
                self.write(self.tokenized[self.pointer])
                self.pointerIncrement()
            # (',', varName)*
            while self.getCode(self.tokenized[self.pointer]) != ';':
                self.write(self.tokenized[self.pointer])
                self.pointerIncrement()
            # ';'
            self.write(self.tokenized[self.pointer])
            self.pointerIncrement()
            self.idNum -= 1
            self.write('</varDec>')

    def parse(self, tokenized: List[str]):
        self.tokenized = tokenized[1:-1]
        for i in range(len(self.tokenized)):
            self.tokenized[i] = self.tokenized[i].strip('\n')

        # a jack file is a class
        if self.getCode(self.tokenized[self.pointer]) == 'class':
            self.compileClass()

    def writeToFile(self, outputFilePath):
        with open(outputFilePath, 'w') as f:
            f.writelines(self.xml)
        f.close()
