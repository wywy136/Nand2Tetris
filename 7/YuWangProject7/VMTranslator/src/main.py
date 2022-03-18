import sys
from typing import List


dic = {
    'add': ["@SP", "AM=M-1", "D=M", "@SP", "AM=M-1", "M=M+D", "@SP", "M=M+1"],
    'sub': ["@SP", "AM=M-1", "D=M", "@SP", "AM=M-1", "M=M-D", "@SP", "M=M+1"],
    'and': ["@SP", "AM=M-1", "D=M", "@SP", "AM=M-1", "M=M&D", "@SP", "M=M+1"],
    'or': ["@SP", "AM=M-1", "D=M", "@SP", "AM=M-1", "M=M|D", "@SP", "M=M+1"],
    'not': ["@SP", "AM=M-1", "M=!M", "@SP", "M=M+1"],
    'neg': ["@SP", "AM=M-1", "M=-M", "@SP", "M=M+1"]
}

simple_arith = ['add', 'sub', 'and', 'or', 'not', 'neg']
jmp_sign = {
    'eq': 'JEQ',
    'lt': 'JLT',
    'gt': 'JGT'
}
label_dic = {
    'argument': 'ARG',
    'local': 'LCL',
    'this': 'THIS',
    'that': 'THAT'
}
pointer_dic = {
    '0': 'THIS',
    '1': 'THAT'
}


def cleanText(assembly: List[str]):

    target = []
    isCommentLine = False
    invalidElements = ['\t', '\n']
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


def generate_arith(sign, jmp, end):
    return [
        "@SP",
        "AM=M-1",
        "D=M",
        "@SP",
        "AM=M-1",
        "D=M-D",
        "@" + jmp,
        "D;" + sign,
        "@SP",
        "A=M",
        "M=0",
        "@" + end,
        "0;JMP",
        "(" + jmp + ")",
        "@SP",
        "A=M",
        "M=-1",
        "(" + end + ")",
        "@SP",
        "M=M+1"
    ]


def generate_const(const):
    return [
        "@" + const,
        "D=A",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1"
    ]


def generate_push_1(label: str, num: str):
    return [
        "@" + label,
        "D=M",
        "@" + num,
        "A=D+A",
        "D=M",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1"
    ]


def generate_push_2(label: str):
    return [
        "@" + pointer_dic[label],
        "D=M",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1"
    ]


def generate_push_3(num: str):
    reg_num = 5 + int(num)

    return [
        "@R" + str(reg_num),
        "D=M",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1"
    ]


def generate_push_4(num: str):
    return [
        "@Static" + num,
        "D=M",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1"
    ]


def generate_pop_1(label: str, num: str):
    return [
        "@" + label,
        "D=M",
        "@" + num,
        "D=D+A",
        "@R13",
        "M=D",
        "@SP",
        "AM=M-1",
        "D=M",
        "@R13",
        "A=M",
        "M=D"
    ]


def generate_pop_2(label: str):
    return [
        "@SP",
        "AM=M-1",
        "D=M",
        "@" + pointer_dic[label],
        "M=D"
    ]


def generate_pop_3(num: str):
    reg_num = 5 + int(num)
    return [
        "@SP",
        "AM=M-1",
        "D=M",
        "@R" + str(reg_num),
        "M=D"
    ]


def generate_pop_4(num: str):
    return [
        "@Static" + num,
        "D=A",
        "@R13",
        "M=D",
        "@SP",
        "M=M-1",
        "A=M",
        "D=M",
        "@R13",
        "A=M",
        "M=D"
    ]


def translator(asm: List[str]) -> List[str]:
    result = []
    label_num = 0
    for line in asm:
        result.append('// ' + line)
        eles = line.strip().split(' ')
        if len(eles) == 1:  # arithmetic
            if eles[0] in simple_arith:
                result += dic[eles[0]]
            else:
                jmp_label = 'JMP' + str(label_num)
                end_label = 'END' + str(label_num)
                label_num += 1
                sign = jmp_sign[eles[0]]
                result += generate_arith(sign, jmp_label, end_label)
        else:  # stack operation
            if eles[1] == "constant":  # push constant
                result += generate_const(eles[2])
            elif eles[0] == "push":
                if eles[1] in ['argument', 'local', 'this', 'that']:
                    label = label_dic[eles[1]]
                    num = eles[2]
                    result += generate_push_1(label, num)
                elif eles[1] == 'pointer':  # pointer 0/1
                    label = eles[2]
                    result += generate_push_2(label)
                elif eles[1] == 'temp':  # temp
                    num = eles[2]
                    result += generate_push_3(num)
                else:  # static
                    num = eles[2]
                    result += generate_push_4(num)
            else:  # pop
                if eles[1] in ['argument', 'local', 'this', 'that']:
                    label = label_dic[eles[1]]
                    num = eles[2]
                    result += generate_pop_1(label, num)
                elif eles[1] == 'pointer':  # pointer 0/1
                    label = eles[2]
                    result += generate_pop_2(label)
                elif eles[1] == 'temp':  # temp
                    num = eles[2]
                    result += generate_pop_3(num)
                else:  # static
                    num = eles[2]
                    result += generate_pop_4(num)

    return result


def main(args):
    filepath = '/'.join(args[1].split('/')[0:-1])
    infilename = args[1].split('/')[-1]
    outfilepath = filepath + '/' + infilename.split('.')[0] + '.asm'

    with open(args[1], 'r') as f:
        vm = f.readlines()

    cleaned_vm = cleanText(vm)
    # print(cleaned_vm)
    asm = translator(cleaned_vm)

    for i in range(len(asm)):
        asm[i] += '\n'

    with open(outfilepath, 'w') as f:
        f.writelines(asm)
    f.close()


if __name__ == "__main__":
    main(sys.argv)
