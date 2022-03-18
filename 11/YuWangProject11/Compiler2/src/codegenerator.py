from typing import List
from references import Expressions
from vmwriter import VMWriter


class CodeGenerator:
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
        # result VM code
        self.vmWriter = VMWriter()
        # Compiling Variables
        self.classScopeVarTable = []
        self.methodScopeVarTable = []
        self.varNum = {
            'this': 0,
            'static': 0,
            'local': 0,
            'argument': 0
        }
        self.className = None
        self.binaryOpActions = {
            '+': 'add',
            '-': 'sub',
            '*': 'call Math.multiply 2',
            '/': 'call Math.divide 2',
            '&': 'and',
            '|': 'or',
            '<': 'lt',
            '>': 'gt',
            '=': 'eq'
        }
        self.labelCount = 0
        self.fieldCount = 0

    def getSymbol(self, varName):
        for symbol in self.methodScopeVarTable:
            if symbol[0] == varName:
                return symbol

        for symbol in self.classScopeVarTable:
            if symbol[0] == varName:
                return symbol

    def getLabel(self):
        label = f'L{self.labelCount}'
        self.labelCount += 1
        return label

    def getLocalNum(self):
        return self.varNum['local']

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

    def compileClass(self):
        self.write('<class>')
        # 'class', classname, '{'
        self.idNum += 1
        for i in range(3):
            # record className
            if i == 1:
                self.className = self.getCode(self.tokenized[self.pointer])
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
            # add variables to classSopceVarTable
            order = 0
            varKind = None
            varType = None
            varName = None
            while self.getCode(self.tokenized[self.pointer]) != ';':
                self.write(self.tokenized[self.pointer])
                if order == 0:
                    varKind = self.getCode(self.tokenized[self.pointer])
                    if varKind == 'field':
                        varKind = 'this'
                if order == 1:
                    varType = self.getCode(self.tokenized[self.pointer])
                if order > 1:
                    varName = self.getCode(self.tokenized[self.pointer])
                    self.classScopeVarTable.append(
                        [
                            varName,
                            varType,
                            varKind,
                            self.varNum[varKind]
                        ]
                    )
                    if varKind == 'this':
                        self.fieldCount += 1
                    self.varNum[varKind] += 1
                self.pointerIncrement()
                order += 1
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
            # If a method, should add an extra 'this' parameter
            isMethod = False
            subroutineType = None
            subroutineClass = self.className
            subroutineName = None
            # ('constructor'|'function'|'method'), ('void'|type), subroutineName, '('
            for i in range(4):
                if i == 0:
                    subroutineType = self.getCode(self.tokenized[self.pointer])
                if i == 2:
                    subroutineName = self.getCode(self.tokenized[self.pointer])
                if self.getCode(self.tokenized[self.pointer]) == "method":
                    isMethod = True
                self.write(self.tokenized[self.pointer])
                self.pointerIncrement()
            # parameterList
            self.compileParameterList(isMethod)
            # ')'
            self.write(self.tokenized[self.pointer])
            self.pointerIncrement()
            # subroutineBody
            self.compileSubroutineBody(subroutineType, subroutineClass, subroutineName)

            self.idNum -= 1
            self.write('</subroutineDec>')

    def compileSubroutineBody(self, subroutineType, subroutineClass, subroutineName):
        self.write('<subroutineBody>')
        self.idNum += 1
        # '{'
        self.write(self.tokenized[self.pointer])
        self.pointerIncrement()
        # verDec*
        self.compileVarDec()

        localVarNum = self.labelCount
        self.vmWriter.write_function(subroutineClass, subroutineName, localVarNum)

        # constructor
        if subroutineType == 'constructor':
            self.vmWriter.write_int(self.fieldCount)
            self.vmWriter.write_call('Memory', 'alloc', '1')
            # Set 'this' to the base address returned by alloc
            self.vmWriter.write('pop pointer 0')
        elif subroutineType == 'method':
            # set 'this' to the base address of the object on which this method
            # was called to operate
            self.vmWriter.write('push argument 0')
            self.vmWriter.write('pop pointer 0')

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
        varName = None
        for i in range(2):
            if i == 1:
                varName = self.getCode(self.tokenized[self.pointer])
            self.write(self.tokenized[self.pointer])
            self.pointerIncrement()
        symbol = self.getSymbol(varName)
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
            # add base and index
            self.vmWriter.write(f'push {symbol[2]} {symbol[3]}')
            self.vmWriter.write('add')
            # expression
            self.compileExpression()
            # Store assigned value in temp
            self.vmWriter.write('pop temp 0')
            # Restore destination
            self.vmWriter.write('pop pointer 1')
            # Restore assigned value
            self.vmWriter.write('push temp 0')
            # Store in target
            self.vmWriter.write('pop that 0')
            # ';'
            self.write(self.tokenized[self.pointer])
            self.pointerIncrement()

        else:
            # '='
            self.write(self.tokenized[self.pointer])
            self.pointerIncrement()
            # expression
            self.compileExpression()
            # write var
            self.vmWriter.write(f'push {symbol[2]} {symbol[3]}')
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

        falseLabel = self.getLabel()
        endLabel = self.getLabel()
        self.vmWriter.write_if(falseLabel)
        # statements
        self.compileStatements()
        # goto
        self.vmWriter.write(f'goto {endLabel}')
        # false-branch
        self.vmWriter.write_label(falseLabel)
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

        whileLabel = self.getLabel()
        falseLabel = self.getLabel()
        self.vmWriter.write_label(whileLabel)
        # expression
        self.compileExpression()
        # ')', '{'
        for i in range(2):
            self.write(self.tokenized[self.pointer])
            self.pointerIncrement()
        # if-goto falseLabel
        self.vmWriter.write_if(falseLabel)
        # statements
        self.compileStatements()
        # goto whileLabel
        self.vmWriter.write(f'goto {whileLabel}')
        # label falseLabel
        self.vmWriter.write_label(falseLabel)
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
        # pop temp 0
        self.vmWriter.write("pop temp 0")
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
        # return;
        else:
            self.vmWriter.write_int(0)
        # write return
        self.vmWriter.write('return')
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
            op = self.getCode(self.tokenized[self.pointer])
            self.write(self.tokenized[self.pointer])
            self.pointerIncrement()
            # term
            self.compileTerm()
            # write op
            self.vmWriter.write(self.binaryOpActions[op])

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
                # write unary op
                if self.getCode(self.tokenized[self.pointer]) == '-':
                    self.vmWriter.write('neg')
                elif self.getCode(self.tokenized[self.pointer]) == '~':
                    self.vmWriter.write('not')

            elif (self.getType(self.tokenized[self.pointer]) in ['integerConstant', 'stringConstant']) or \
                    (self.getCode(self.tokenized[self.pointer]) in Expressions.kwConstant):
                # integer
                if self.getType(self.tokenized[self.pointer]) == 'integerConstant':
                    self.vmWriter.write_int(self.getType(self.tokenized[self.pointer]))
                # string
                elif self.getType(self.tokenized[self.pointer]) == 'stringConstant':
                    self.vmWriter.write_string(self.getCode(self.tokenized[self.pointer]))
                elif self.getCode(self.tokenized[self.pointer]) in Expressions.kwConstant:
                    if self.getCode(self.tokenized[self.pointer]) == 'this':
                        self.vmWriter.write('push pointer 0')
                    else:
                        # null / false
                        self.vmWriter.write_int(0)
                        if self.getCode(self.tokenized[self.pointer]) == 'true':
                            self.vmWriter.write('not')

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
                varName = self.getCode(self.tokenized[self.pointer])
                symbol = self.getSymbol(varName)
                self.write(self.tokenized[self.pointer])
                self.pointerIncrement()
                if self.getCode(self.tokenized[self.pointer]) == '[':
                    # '['
                    self.write(self.tokenized[self.pointer])
                    self.pointerIncrement()
                    # expression
                    self.compileExpression()
                    # write base
                    self.vmWriter.write(f"push {symbol[2]} {symbol[3]}")
                    # add
                    self.vmWriter.write('add')
                    # rebase 'that' to point to var+index
                    self.vmWriter.write('pop pointer 1')
                    self.vmWriter.write('push that 0')
                    # ']'
                    self.write(self.tokenized[self.pointer])
                    self.pointerIncrement()
                else:
                    self.vmWriter.write(f"push {symbol[2]} {symbol[3]}")
        except:
            print(len(self.tokenized), self.pointer)

        self.idNum -= 1
        self.write('</term>')

    def compileSubroutineCall(self):
        # (className | varName) | subroutineName
        funcObj = self.getCode(self.tokenized[self.pointer])
        funcObjSymbol = self.getSymbol(funcObj)
        self.write(self.tokenized[self.pointer])
        self.pointerIncrement()

        # default function name is funcObj, class is this class
        funcName = funcObj
        funcClass = self.className
        default_call = True
        arg_count = 0

        # case： '.'
        if self.getCode(self.tokenized[self.pointer]) == '.':
            default_call = False
            # '.'
            self.write(self.tokenized[self.pointer])
            self.pointerIncrement()
            # try to load the object of the method
            funcObj = self.getSymbol(funcObj)
            funcName = self.getCode(self.tokenized[self.pointer])
            # subroutineName
            self.write(self.tokenized[self.pointer])
            self.pointerIncrement()
            if funcObj:
                # get class of this func
                funcClass = funcObjSymbol[1]
                arg_count = 1
                self.vmWriter.write(f"push {funcObjSymbol[2]} {funcObjSymbol[3]}")
            else:
                funcClass = funcObj

        # case: '('
        if self.getCode(self.tokenized[self.pointer]) == '(':
            if default_call:
                arg_count = 1
                # push this object, should be in
                self.vmWriter.write('push pointer 0')
            # '('
            self.write(self.tokenized[self.pointer])
            self.pointerIncrement()
            # expressionList
            arg_count += self.compileExpressionList()
            # function call
            self.vmWriter.write_call(funcClass, funcName, arg_count)
            # ')'
            self.write(self.tokenized[self.pointer])
            self.pointerIncrement()

    def compileExpressionList(self):
        num = 0
        self.write('<expressionList>')
        self.idNum += 1
        # no expression
        if self.getCode(self.tokenized[self.pointer]) == ')':
            self.idNum -= 1
            self.write('</expressionList>')
            return 0
        # expression
        self.compileExpression()
        num += 1
        # (',', expression)*
        while self.getCode(self.tokenized[self.pointer]) != ')':
            # ','
            self.write(self.tokenized[self.pointer])
            self.pointerIncrement()
            # expression
            self.compileExpression()
            num += 1
        self.idNum -= 1
        self.write('</expressionList>')
        return num

    def compileParameterList(self, isMethod):
        self.write('<parameterList>')
        self.idNum += 1
        # if a method, add 'this'
        if isMethod:
            self.methodScopeVarTable.append(
                [
                    'this',
                    self.className,
                    'argument',
                    self.varNum['argument']
                ]
            )
            self.varNum['argument'] += 1

        # not reach the end of the list
        order = 0
        varName = None
        varType = None
        while self.getCode(self.tokenized[self.pointer]) != ')':
            # argType
            if order % 3 == 0:
                varName = self.getCode(self.tokenized[self.pointer])
            # argName
            if order % 3 == 1:
                varType = self.getCode(self.tokenized[self.pointer])
                self.methodScopeVarTable.append([
                    varName,
                    varType,
                    'argument',
                    self.varNum['argument']
                ])
                self.varNum['argument'] += 1

            self.write(self.tokenized[self.pointer])
            self.pointerIncrement()
            order += 1
        self.idNum -= 1
        self.write('</parameterList>')

    def compileVarDec(self):
        # one or more lines or varDec
        varType = None
        while self.getCode(self.tokenized[self.pointer]) == 'var':
            self.write('<varDec>')
            self.idNum += 1
            # 'var', typename, varname
            varName = None
            for i in range(3):
                if i == 1:
                    varType = self.getCode(self.tokenized[self.pointer])
                if i == 2:
                    varName = self.getCode(self.tokenized[self.pointer])
                    self.methodScopeVarTable.append([
                        varName,
                        varType,
                        'local',
                        self.varNum['local']
                    ])
                    self.varNum['local'] += 1

                self.write(self.tokenized[self.pointer])
                self.pointerIncrement()
            # (',', varName)*
            while self.getCode(self.tokenized[self.pointer]) != ';':
                # not a comma -> a new variable in the same line of jack
                if self.getCode(self.tokenized[self.pointer]) != ',':
                    varName = self.getCode(self.tokenized[self.pointer])
                    self.methodScopeVarTable.append([
                        varName,
                        varType,
                        'local',
                        self.varNum['local']
                    ])
                    self.varNum['local'] += 1

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
            f.writelines(self.vmWriter.VM)
        f.close()
