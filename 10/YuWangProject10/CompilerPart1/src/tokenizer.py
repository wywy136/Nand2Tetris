from typing import List
from references import Lexical


class Tokenizer:
    def __init__(self):
        self.outFilePath = None
        self.tokenized = ['<tokens>']
        self.invalidElements = {'\t', '\n'}
        self.partIC = ''
        self.partID = ''
        self.partSC = ''
        self.inString = False

    def deComment(self, jack: List[str]):

        target = []
        isCommentLine = False

        def isBlankLine(line: str) -> bool:
            for c in line:
                if c not in self.invalidElements:
                    return False
            return True

        for line in jack:
            # recognize comment lines
            if line.startswith("/*"):
                isCommentLine = True

            # recognize the end of comments
            if line.endswith("*/\n"):
                isCommentLine = False
                continue

            # skip comment line
            if isCommentLine:
                continue

            if line.startswith("//"):
                continue

            # skip a blank line when it is not a comment line
            if isBlankLine(line):
                continue

            line_removed = ""
            for i, c in enumerate(line):
                # reaches the comment
                if i < len(line) - 1 and c == '/' and line[i + 1] == '/':
                    break
                # remove ' ', '\t' and '\n'
                if c in self.invalidElements:
                    continue
                line_removed += c

            # line_removed += '\n'
            target.append(line_removed)

        return target

    def reset(self):
        self.partIC = ''
        self.partID = ''
        self.partSC = ''
        self.inString = False

    def partOfId(self, char: str):
        if char.isdigit() or self.isLetter(char) or char == '_':
            return True
        return False

    def writeSymbol(self, symbol: str):
        if symbol in Lexical.symbolReplacement:
            self.tokenized.append('<symbol> ' + Lexical.symbolReplacement[symbol] + ' </symbol>')
        else:
            self.tokenized.append('<symbol> ' + symbol + ' </symbol>')

    def writeKeyword(self, keyword: str):
        self.tokenized.append('<keyword> ' + keyword + ' </keyword>')

    def writeInt(self, integer: str):
        self.tokenized.append('<integerConstant> ' + integer + ' </integerConstant>')

    def writeString(self, string: str):
        self.tokenized.append('<stringConstant> ' + string + ' </stringConstant>')

    def writeID(self, identifier: str):
        self.tokenized.append('<identifier> ' + identifier + ' </identifier>')

    def getTokenization(self):
        return self.tokenized

    def writeFile(self):
        assert self.outFilePath is not None

        for i in range(len(self.tokenized)):
            self.tokenized[i] += '\n'

        with open(self.outFilePath, 'w') as f:
            f.writelines(self.tokenized)
        f.close()

    def isLetter(self, c):
        asc = ord(c)
        if asc in range(65, 91) or asc in range(97, 123):
            return True
        return False

    def tokenize(self, inFilePath):

        with open(inFilePath, 'r') as f:
            jack = f.readlines()

        # print(inFilePath[:-5])
        self.outFilePath = inFilePath[:-5] + 'T.xml'
        # print(self.outFilePath)

        noComment = self.deComment(jack)

        for line in noComment:
            segs: List[str] = line.split(' ')

            for seg in segs:
                if seg in Lexical.keyword:
                    self.writeKeyword(seg)
                elif seg in Lexical.symbol:
                    self.writeSymbol(seg)
                elif self.inString and '"' not in seg:
                    self.partSC += ' ' + seg
                # elif self.inString and seg.startswith('"'):
                #     self.partSC += ' '
                else:
                    for i, c in enumerate(seg):
                        # a symbol
                        if c in Lexical.symbol:
                            self.writeSymbol(c)
                            self.reset()
                        # a number not being a part of ID
                        elif c.isdigit() and len(self.partID) == 0:
                            self.partIC += c
                            if i == len(seg) - 1 or not seg[i + 1].isdigit():
                                self.writeInt(self.partIC)
                                self.reset()
                        elif c.isdigit() and len(self.partID) > 0:
                            self.partID += c
                        # a number in an int const
                        elif c.isdigit() and i < len(seg) - 1 and seg[i + 1].isdigit():
                            self.partIC += c
                        # a number at the end of an int const
                        # elif c.isdigit() and (i == len(seg) - 1 or not seg[i + 1].isdigit()):
                        #     self.partIC += c
                        #     self.writeInt(self.partIC)
                        #     self.reset()
                        # start of a string const
                        elif c == '"' and not self.inString:
                            self.inString = True
                        # end of a string const
                        elif c == '"' and self.inString:
                            if i == 0:
                                self.partSC += ' '
                            self.writeString(self.partSC)
                            self.reset()
                        # a char in a string const
                        elif self.inString:
                            self.partSC += c
                        # must be a char
                        else:
                            self.partID += c
                            if i == len(seg) - 1 or not self.partOfId(seg[i + 1]):
                                # e.x., (true), return;,
                                if self.partID in Lexical.keyword:
                                    self.writeKeyword(self.partID)
                                else:
                                    self.writeID(self.partID)
                                self.reset()

        self.tokenized.append('</tokens>')
