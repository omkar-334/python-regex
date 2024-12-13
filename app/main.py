import sys


def tokenize(pattern):
    tokens = []

    i = 0
    while True:
        if i >= len(pattern):
            break
        if pattern[i] == "\\":
            token = pattern[i : i + 2]
            i += 2
        elif pattern[i].isspace():
            token = pattern[i]
            i += 1
        elif pattern[i] == "[":
            group = []
            while i < len(pattern) and pattern[i] != "]":
                group.append(pattern[i])
                i += 1
            group.append("]")
            i += 1
            token = "".join(group)
        else:
            literal = []
            while i < len(pattern) and not pattern[i].isspace() and pattern[i] != "\\":
                literal.append(pattern[i])
                i += 1
            token = "".join(literal)
        tokens.append(token)
    return tokens


def match(string, tokens):
    if not tokens:
        return True

    if not string:
        return False

    curr = tokens[0]

    for i in range(len(string)):
        if curr == "\\w":
            if string[i].isalnum() or string[0] == "_":
                return match(string[1:], tokens[1:])
            else:
                return match(string[1:], tokens)
        elif curr == "\\d":
            if string[i].isdigit():
                return match(string[1:], tokens[1:])
            else:
                return match(string[1:], tokens)
        elif curr == " ":
            if string[i].isspace():
                return match(string[1:], tokens[1:])
            else:
                return match(string[1:], tokens)
        elif curr.startswith("[") and curr.endswith("]"):
            curr = curr[1:-1]
            if curr[0] == "^":
                curr = curr[1:]
                return not any(i in string for i in curr)
            else:
                return any(i in string for i in curr)
        else:
            if string.startswith(curr):
                curridx = len(curr)
                return match(string[curridx:], tokens[1:])
            else:
                return match(string[1:], tokens)

    return False


def match_pattern(input_line, pattern):
    if len(pattern) == 1:
        return pattern in input_line

    tokens = tokenize(pattern)

    return match(input_line, tokens)


def main():
    pattern = sys.argv[2]
    input_line = sys.stdin.read()

    if sys.argv[1] != "-E":
        print("Expected first argument to be '-E'")
        exit(1)

    if match_pattern(input_line, pattern):
        exit(0)
    else:
        exit(1)


if __name__ == "__main__":
    main()
