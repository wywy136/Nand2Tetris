import sys
from typing import List

# A dict for mapping the symbol/variables to RAM address
symbol_table = {
    'SP': 0,
    'LCL': 1,
    'ARG': 2,
    'THIS': 3,
    'THAT': 4,
    'SCREEN': 16384,
    'KBD': 24576,
    'R0': 0,
    'R1': 1,
    'R2': 2,
    'R3': 3,
    'R4': 4,
    'R5': 5,
    'R6': 6,
    'R7': 7,
    'R8': 8,
    'R9': 9,
    'R10': 10,
    'R11': 11,
    'R12': 12,
    'R13': 13,
    'R14': 14,
    'R15': 15
}

dest_table = {
    '': '000',
    'M': '001',
    'D': '010',
    'MD': '011',
    'A': '100',
    'AM': '101',
    'AD': '110',
    'AMD': '111'
}

jump_table = {
    '': '000',
    'JGT': '001',
    'JEQ': '010',
    'JGE': '011',
    'JLT': '100',
    'JNE': '101',
    'JLE': '110',
    'JMP': '111'
}

comp_table = {
    '0': '0101010',
    '1': '0111111',
    '-1': '0111010',
    'D': '0001100',
    'A': '0110000',
    'M': '1110000',
    '!D': '0001101',
    '!A': '0110001',
    '!M': '1110001',
    '-D': '0001111',
    '-A': '0110011',
    '-M': '1110011',
    'D+1': '0011111',
    'A+1': '0110111',
    'M+1': '1110111',
    'D-1': '0001110',
    'A-1': '0110010',
    'M-1': '1110010',
    'D+A': '0000010',
    'D+M': '1000010',
    'D-A': '0010011',
    'D-M': '1010011',
    'A-D': '0000111',
    'M-D': '1000111',
    'D&A': '0000000',
    'D&M': '1000000',
    'D|A': '0010101',
    'D|M': '1010101'
}


# same as project 1
def cleanText(assembly: List[str]):

    target = []
    isCommentLine = False
    invalidElements = [' ', '\t', '\n']
    invalidElements = set(invalidElements)

    # returns true if a line is black
    # if a line is not a part of comment and contains chars other than ' ', '\t', '\n'
    # it should not be a blank line
    def isBlankLine(line: str) -> bool:
        for c in line:
            if c not in invalidElements:
                return False
        return True

    for line in assembly:
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
            if c in invalidElements:
                continue
            line_removed += c

        # line_removed += '\n'
        target.append(line_removed)

    return target


# remove symbols from the code and record the line number
def remove_symbols(asm: List[str]):
    line_num = 0
    removed_asm = []
    for line in asm:
        if line[0] == '(':
            symbol = line[1:-1]
            if symbol not in symbol_table:
                symbol_table[symbol] = line_num
                line_num -= 1
        else:
            removed_asm.append(line)
        line_num += 1

    return removed_asm


# add variables
def parce_variables(asm: List[str]):
    variable_line = 16
    for line in asm:
        if line[0] == '@':
            variable = line[1:]

            is_variable = True
            if variable[0].isdigit():
                is_variable = False

            if is_variable and variable not in symbol_table:
                symbol_table[variable] = variable_line
                variable_line += 1


# assembly -> machine language
def translate(asm: List[str]):
    res = []
    for i, line in enumerate(asm):
        # A-instruction
        if line[0] == '@':
            if line[1:] in symbol_table:
                addr = bin(symbol_table[line[1:]])[2:]
            else:
                addr = bin(int(line[1:]))[2:]
            addr = '0' * (16 - len(addr)) + addr + '\n'
            res.append(addr)
        # C-instruction
        else:
            d = ''
            if '=' in line:
                d = line.split('=')[0]
            dest = dest_table[d]

            j = ''
            if ';' in line:
                j = line.split(';')[1]
            jump = jump_table[j]

            c = ''
            if '=' in line:
                c = line.split('=')[1]
            elif ';' in line:
                c = line.split(';')[0]
            comp = comp_table[c]

            ins = '111' + comp + dest + jump + '\n'
            res.append(ins)

    return res


def main(args):
    filepath = '/'.join(args[1].split('/')[0:-1])
    infilename = args[1].split('/')[-1]
    outfilepath = filepath + '/' + infilename.split('.')[0] + '.hack'

    with open(args[1], 'r') as f:
        assembly = f.readlines()

    cleaned_asm = cleanText(assembly)
    removed_asm = remove_symbols(cleaned_asm)
    parce_variables(removed_asm)
    machine_language = translate(removed_asm)
    # print(assembly)

    with open(outfilepath, 'w') as f:
        f.writelines(machine_language)
    f.close()


if __name__ == "__main__":
    main(sys.argv)
