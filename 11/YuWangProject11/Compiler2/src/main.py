from tokenizer import Tokenizer
from codegenerator import CodeGenerator

import os
import sys


def main(args):
    t = Tokenizer()
    g = CodeGenerator()
    # path: a file or a directory
    path: str = args[1]
    # print(path)

    # a file path
    if path.endswith('.jack'):
        vmPath = path[:-4] + 'vm'
        t.tokenize(path)
        t.writeFile()
        tokenization = t.getTokenization()
        g.parse(tokenization)
        g.writeToFile(vmPath)

    # a directory path
    else:
        if path.endswith('/'):
            path = path[:-1]

        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith('.jack'):
                    filepath = path + '/' + file
                    vmPath = path + '/' + file[:-4] + 'vm'
                    t.tokenize(filepath)
                    tokenization = t.getTokenization()
                    t.writeFile()
                    g.parse(tokenization)
                    g.writeToFile(vmPath)
                    t.reset()
                    g.clearState()


if __name__ == '__main__':
    main(sys.argv)
