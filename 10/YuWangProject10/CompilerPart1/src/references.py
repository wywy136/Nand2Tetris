from typing import Set


class Lexical:
    keyword = {
        'class',
        'constructor',
        'function',
        'method',
        'field',
        'static',
        'var',
        'int',
        'char',
        'boolean',
        'void',
        'true',
        'false',
        'null',
        'this',
        'let',
        'do',
        'if',
        'else',
        'while',
        'return'
    }

    symbol = {
        '{',
        '}',
        '(',
        ')',
        '[',
        ']',
        '.',
        ',',
        ';',
        '+',
        '-',
        '*',
        '/',
        '&',
        '|',
        '<',
        '>',
        '=',
        '~'
    }

    symbolReplacement = {
        '<': '&lt;',
        '>': '&gt;',
        '&': '&amp;'
    }


class Expressions:
    op: Set = {
        '+',
        '-',
        '*',
        '/',
        '&amp;',
        '|',
        '&lt;',
        '&gt;',
        '='
    }

    unaryOp: Set = {
        '-',
        '~'
    }

    kwConstant: Set = {
        'true',
        'false',
        'null',
        'this'
    }