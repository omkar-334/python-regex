import sys

d = dict(
    anchors=["^", "$"],
    quantifiers=["+", "?"],
    space=[" "],
    wildcard=["."],
    escape=["\\"],
)


def tokenize(pattern):
    tokens = []
    i = 0

    while True:
        if i >= len(pattern):
            break
        if pattern[i] in d["anchors"] + d["space"] + d["wildcard"]:
            token = pattern[i]
            i += 1
        elif pattern[i] in d["quantifiers"]:
            prev_token = tokens.pop()
            token = prev_token[-1] + pattern[i]

            prev_token = prev_token[:-1]
            if prev_token:
                tokens.append(prev_token)

            i += 1

        elif pattern[i] == "\\":
            token = pattern[i : i + 2]
            i += 2
        elif pattern[i] == "(":
            group = []
            i += 1
            while i < len(pattern) and pattern[i] != ")":
                group.append(pattern[i])
                i += 1
            token = "(" + "".join(group) + ")"
            i += 1
        elif pattern[i] == "[":
            group = []
            i += 1
            while i < len(pattern) and pattern[i] != "]":
                group.append(pattern[i])
                i += 1
            token = "[" + "".join(group) + "]"
            i += 1
        else:
            literal = []
            while i < len(pattern) and pattern[i] not in [i for lst in d.values() for i in lst]:
                literal.append(pattern[i])
                i += 1
            token = "".join(literal)
        tokens.append(token)

    start = tokens[0] == "^"
    end = tokens[-1] == "$"
    if start:
        tokens.pop(0)
    if end:
        tokens.pop()

    return tokens, start, end


def tokenize_alternation(token):
    token = token[1:-1]
    patterns = token.split("|")
    output = []
    for i in patterns:
        output.append(tokenize(i))
    return output


def match(string, tokens, start, end):
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
        elif curr.startswith("(") and curr.endswith(")"):
            patterns = tokenize_alternation(curr)
            return any(match(string, i[0], i[1], i[2]) for i in patterns)
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
            rep = curr[0]
            count = 0
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

    tokens, start, end = tokenize(pattern)
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
