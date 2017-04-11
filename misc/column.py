from pyparsing import Literal, Word, Combine, Optional, Suppress, delimitedList, oneOf, alphas, nums

ESC = Literal('\x1b')
integer = Word(nums)
escapeSeq = Combine(ESC + '[' + Optional(delimitedList(integer, ';')) + oneOf(list(alphas)))


def nonAnsiString(s):
    return Suppress(escapeSeq).transformString(s)


def column(array2d, padding=2, delimiter=' '):
    pad_string = delimiter * padding
    widths = [max(map(len, map(nonAnsiString, col))) for col in zip(*array2d)]
    result = []
    for row in array2d:
        items = []
        for val, width in zip(row, widths):
            extra_len = len(val) - len(nonAnsiString(val))
            items.append(val.ljust(width + extra_len))
        line = pad_string.join(items)
        result.append(line)
    return result
