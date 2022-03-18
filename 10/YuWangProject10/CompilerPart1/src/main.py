from tokenizer import Tokenizer
from parser import Parser

import os
import sys


def main(args):
    t = Tokenizer()
    p = Parser()
    # path: a file or a directory
    path: str = args[1]
    # print(path)

    # a file path
    if path.endswith('.jack'):
        xmlPath = path[:-4] + 'xml'
        t.tokenize(path)
        t.writeFile()
        tokenization = t.getTokenization()
        p.parse(tokenization)
        p.writeToFile(xmlPath)

    # a directory path
    else:
        if path.endswith('/'):
            path = path[:-1]

        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith('.jack'):
                    filepath = path + '/' + file
                    xmlPath = path + '/' + file[:-4] + 'xml'
                    t.tokenize(filepath)
                    tokenization = t.getTokenization()
                    t.writeFile()
                    p.parse(tokenization)
                    p.writeToFile(xmlPath)
                    t.reset()
                    p.clearState()


if __name__ == '__main__':
    main(sys.argv)
