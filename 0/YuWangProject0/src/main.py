import sys


def cleanText(args):
    # filepath
    filepath = '/'.join(args[1].split('/')[0:-1])
    infilename = args[1].split('/')[-1]
    outfilepath = filepath + '/' + infilename.split('.')[0] + '.out'

    # read each line of input file
    with open(args[1], 'r') as f:
        content = f.readlines()

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

    for line in content:
        # recognize comment lines
        if line.startswith("/*") or line.startswith("//"):
            isCommentLine = True

        # recognize the end of comments
        if line.endswith("*/\n"):
            isCommentLine = False
            continue

        # skip comment line
        if isCommentLine:
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

        # add a new '\n' for each line
        line_removed += '\n'
        target.append(line_removed)

    with open(outfilepath, 'w') as f:
        f.writelines(target)


if __name__ == "__main__":
    cleanText(sys.argv)
