import sys


def tokenize(pattern):
    anchors = ["^", "$"]
    quantifiers = ["+", "?"]
    space = [" "]
    wildcard = ["."]
    meta = anchors + quantifiers + ["\\"] + space + wildcard

    tokens = []
    i = 0

    while True:
        if i >= len(pattern):
            break
        if pattern[i] in anchors + space + wildcard:
            token = pattern[i]
            i += 1
        elif pattern[i] in quantifiers:
            prev_token = tokens.pop()
            token = prev_token[-1] + pattern[i]

            prev_token = prev_token[:-1]
            if prev_token:
                tokens.append(prev_token)

            i += 1

        elif pattern[i] == "\\":
            token = pattern[i : i + 2]
            i += 2
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
            while i < len(pattern) and pattern[i] not in meta:
                literal.append(pattern[i])
                i += 1
            token = "".join(literal)
        tokens.append(token)
    return tokens


def match(string, tokens, start, end):
    print(string, tokens)
    if not tokens:
        if end:
            if not string:
                return True
            return False
        return True

    if not string:
        if len(tokens) == 1 and tokens[0].endswith("?"):
            return True
        return False

    curr = tokens[0]

    for i in range(len(string)):
        if curr == ".":
            return match(string[1:], tokens[1:], start, end)
        elif curr == "\\w":
            if string[i].isalnum() or string[0] == "_":
                return match(string[1:], tokens[1:], start, end)
            else:
                return match(string[1:], tokens, start, end)
        elif curr == "\\d":
            if string[i].isdigit():
                return match(string[1:], tokens[1:], start, end)
            else:
                return match(string[1:], tokens, start, end)
        elif curr == " ":
            if string[i].isspace():
                return match(string[1:], tokens[1:], start, end)
            else:
                return match(string[1:], tokens, start, end)
        elif curr.startswith("[") and curr.endswith("]"):
            curr = curr[1:-1]
            if curr[0] == "^":
                curr = curr[1:]
                return not any(i in string for i in curr)
            else:
                return any(i in string for i in curr)
        elif string.startswith(curr):
            curridx = len(curr)
            return match(string[curridx:], tokens[1:], start, end)
        elif curr in [".*", ".?", ".+"]:
            print("top")
            greedy = curr == ".*"

            if greedy:  # For '.*'
                for j in range(len(string) + 1):
                    if match(string[j:], tokens[1:], start, end):
                        return True
            else:  # For '.?'
                # Match zero characters
                if match(string, tokens[1:], start, end):
                    return True
                if len(string) > 0 and match(string[1:], tokens[1:], start, end):
                    return True
            return False
        elif curr.endswith("+") or curr.endswith("?"):
            print("bottom")
            rep = curr[0]
            count = 0
            print(rep, string)
            for char in string:
                if char == rep:
                    count += 1
                else:
                    break

            if not count:
                if curr.endswith("+"):
                    return False
            return match(string[count:], tokens[1:], start, end)
        else:
            if start:
                return False
            else:
                return match(string[1:], tokens, start, end)

    return False


def match_pattern(input_line, pattern):
    if len(pattern) == 1:
        return pattern in input_line

    tokens = tokenize(pattern)

    if tokens[0] == "^":
        start = True
        tokens = tokens[1:]
    else:
        start = False

    if tokens[-1] == "$":
        end = True
        tokens = tokens[:-1]
    else:
        end = False

    print(tokens, start, end)
    return match(input_line, tokens, start, end)


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
