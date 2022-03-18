import sys
from typing import List
import os


dic = {
    'add': ["@SP", "AM=M-1", "D=M", "@SP", "AM=M-1", "M=M+D", "@SP", "M=M+1"],
    'sub': ["@SP", "AM=M-1", "D=M", "@SP", "AM=M-1", "M=M-D", "@SP", "M=M+1"],
    'and': ["@SP", "AM=M-1", "D=M", "@SP", "AM=M-1", "M=M&D", "@SP", "M=M+1"],
    'or': ["@SP", "AM=M-1", "D=M", "@SP", "AM=M-1", "M=M|D", "@SP", "M=M+1"],
    'not': ["@SP", "AM=M-1", "M=!M", "@SP", "M=M+1"],
    'neg': ["@SP", "AM=M-1", "M=-M", "@SP", "M=M+1"]
}

arith = ['add', 'sub', 'and', 'or', 'not', 'neg', 'eq', 'lt', 'gt']
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


def generate_push_4(file: str, num: str):
    return [
        "@" + file + ".Static" + num,
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


def generate_pop_4(file: str, num: str):
    return [
        "@" + file + ".Static" + num,
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


def generate_function_def(name: str, num_arg: str):
    res = ["(" + name + ")"]
    for i in range(int(num_arg)):
        res += [
            "@SP",
            "A=M",
            "M=0",
            "@SP",
            "M=M+1"
        ]
    return res


def generate_return():
    return [
        # FRAME = LCL
        "@LCL",
        "D=M",
        "@FRAME",
        "M=D",
        # RET = *(FRAME-5)
        "@FRAME",
        "D=M",
        "@5",
        "A=D-A",
        "D=M",
        "@RET",
        "M=D",
        # *ARG = pop()
        "@SP",
        "AM=M-1",
        "D=M",
        "@ARG",
        "A=M",
        "M=D",
        # SP = ARG + 1
        "@ARG",
        "D=M+1",
        "@SP",
        "M=D",
        # THAT = *(FRAME-1)
        "@FRAME",
        "A=M-1",
        "D=M",
        "@THAT",
        "M=D",
        # THIS = *(FRAME-2)
        "@FRAME",
        "D=M",
        "@2",
        "A=D-A",
        "D=M",
        "@THIS",
        "M=D",
        # ARG = *(FRAME-3)
        "@FRAME",
        "D=M",
        "@3",
        "A=D-A",
        "D=M",
        "@ARG",
        "M=D",
        # LCL = *(FRAME-4)
        "@FRAME",
        "D=M",
        "@4",
        "A=D-A",
        "D=M",
        "@LCL",
        "M=D",
        # goto RET
        "@RET",
        "A=M",
        "0;JMP"
    ]


def generate_function_call(func_name: str, label_num: int, arg_num: int = 0):
    mv_num = str(5 + arg_num)
    return [
        "@LABEL" + str(label_num),
        "D=A",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1",
        "@LCL",
        "D=M",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1",
        "@ARG",
        "D=M",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1",
        "@THIS",
        "D=M",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1",
        "@THAT",
        "D=M",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1",
        "@SP",
        "D=M",
        "@" + mv_num,
        "D=D-A",
        "@ARG",
        "M=D",
        "@SP",
        "D=M",
        "@LCL",
        "M=D",
        "@" + func_name,
        "0;JMP",
        "(LABEL" + str(label_num) + ")"
    ]


def translator(asm: List[str], bootstrap: bool) -> List[str]:
    result = []
    label_num = 0
    file = None
    if bootstrap:
        result += ["// Bootstrap", "@256", "D=A", "@SP", "M=D"]
        result += generate_function_call("Sys.init", label_num)
        label_num += 1
    for line in asm:
        if line.startswith("--"):
            file = line.strip()[2:]
        result.append('// ' + line)
        eles = line.strip().split(' ')
        if eles[0] in arith:  # arithmetic
            if eles[0] in simple_arith:
                result += dic[eles[0]]
            else:
                jmp_label = 'JMP' + str(label_num)
                end_label = 'END' + str(label_num)
                label_num += 1
                sign = jmp_sign[eles[0]]
                result += generate_arith(sign, jmp_label, end_label)
        elif eles[0] in ['push', 'pop']:  # stack operation
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
                    result += generate_push_4(file, num)
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
                    result += generate_pop_4(file, num)
        elif eles[0] == 'label':  # label
            lbl = "(" + eles[1] + ")"
            result.append(lbl)
        elif eles[0] == 'goto':  # goto
            jmp = "@" + eles[1]
            result += [jmp, "0;JMP"]
        elif eles[0] == 'if-goto':
            jmp = "@" + eles[1]
            result += [
                "@SP",
                "AM=M-1",
                "D=M",
                jmp,
                "D;JNE"
            ]
        elif eles[0] == 'function':  # function definition
            name, num_lcl = eles[1], eles[2]
            result += generate_function_def(name, num_lcl)
        elif eles[0] == 'return':
            result += generate_return()
        elif eles[0] == 'call':
            name, num_arg = eles[1], eles[2]
            result += generate_function_call(name, label_num, int(num_arg))
            label_num += 1

    return result


def main(args, bootstrap=True):
    if args[1].endswith('/'):
        args[1] = args[1][:-1]
    filepath = args[1]
    infilename = args[1].split('/')[-1]
    outfilepath = filepath + '/' + infilename + '.asm'
    print(infilename)

    # target_vm = []
    # for root, dirs, files in os.walk(filepath):
    #     for file in files:
    #         if file.endswith(".vm"):
    #             # target_vm.append("--" + file)
    #             target_vm.append(os.path.join(root, file))
    #
    # vm = []
    # for f in target_vm:
    #     with open(f, 'r') as file:
    #         # print(f.split('/')[-1].split('.')[0])
    #         vm += ["--" + f.split('/')[-1].split('.')[0]]
    #         vm += file.readlines()
    #
    # cleaned_vm = cleanText(vm)
    # asm = translator(cleaned_vm, bootstrap)
    #
    # for i in range(len(asm)):
    #     asm[i] += '\n'
    #
    # with open(outfilepath, 'w') as f:
    #     f.writelines(asm)
    # f.close()


if __name__ == "__main__":
    main(sys.argv)
