"""
Author: Jyonn
Link: https://github.com/Jyonn/wechat/blob/master/Base/parser.py
"""


class DynamicParser:
    @staticmethod
    def _split(command):
        command = command + ' '
        splits = []
        index = 0
        split_start = 0
        quote = None

        while index < len(command):
            if command[index] == ' ':
                if not quote:
                    split = command[split_start: index]
                    if split:
                        splits.append(split)
                    split_start = index + 1
            elif command[index] == '\\':
                if index + 1 == len(command):
                    raise ValueError('ends with an escape character')
                else:
                    index += 1
            elif command[index] in '"\'':
                if quote:
                    quote = None
                    split = command[split_start: index+1]
                    splits.append(split)
                    split_start = index + 1
                else:
                    quote = command[index]

            index += 1

        if quote:
            raise ValueError("quotes don't match")

        return splits

    @staticmethod
    def _find_all(s: str, c: str):
        index_list = []
        index = s.find(c)
        while index != -1:
            index_list.append(index)
            index = s.find(c, index + 1)
        return index_list

    @classmethod
    def _remove_quote(cls, s: str):
        if not s:
            return s

        if s[-1] in '"\'':
            if s[0] != s[-1]:
                raise ValueError('quotes are not on both ends of the substring')
            return bytes(s[1:-1], "utf-8").decode("unicode_escape")

        quote_indexes = cls._find_all(s, '"')
        quote_indexes.extend(cls._find_all(s, "'"))

        for quote_index in quote_indexes:
            if s[quote_index - 1] != '\\':
                raise ValueError('quotes are not on both ends of the substring')

        return s

    @classmethod
    def _combine(cls, splits: list):
        combines = []

        index = 0
        while index < len(splits):
            split = splits[index]  # type: str
            if split.startswith('--') or split.startswith('—'):  # long
                if split.startswith('--'):
                    split = split[2:]
                else:
                    split = split[1:]
                if not split:
                    raise ValueError('empty parameter name')
                if '=' in split:
                    key, value = split.split('=', maxsplit=1)
                else:
                    key, value = split, None
                combines.append(('--' + key, value))
            elif split.startswith('-'):  # short
                split = split[1:]
                if not split:
                    raise ValueError('empty parameter name')

                key, value = split[0], split[1:] or None
                combines.append(('-' + key, value))
            else:
                combines.append(split)

            index += 1

        for index in range(len(combines)):
            if isinstance(combines[index], tuple):
                combines[index] = (cls._remove_quote(combines[index][0]),
                                   cls._remove_quote(combines[index][1]))
            else:
                combines[index] = cls._remove_quote(combines[index])

        return combines

    @classmethod
    def parse(cls, command):
        splits = cls._split(command)
        combines = cls._combine(splits)
        kwargs = {}
        args = []

        for combine in combines:
            if isinstance(combine, tuple):
                kwargs[combine[0]] = combine[1]
            else:
                args.append(combine)

        return args, kwargs


if __name__ == '__main__':
    print(DynamicParser.parse('ls -l -m3 lang/modal --inside --parent=x shall'))
