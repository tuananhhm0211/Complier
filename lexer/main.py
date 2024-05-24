import json


def readAutomation():
    #read file .dat save graph and end states
    f = open("lexer/automaton.dat", "r")
    graph = dict()
    endstate = dict()
    transitionFlag = False
    endstateFlag = False

    for line in f:
        if line.strip() == "TRANSITIONS":
            transitionFlag = True
            continue
        if line.strip() == "ENDSTATES":
            endstateFlag = True
            continue
        if line.strip() == "":
            transitionFlag = False
        if transitionFlag:
            x = line.split()
            key = x[0]
            if key in graph.keys():
                val = graph[key]
                val[x[1]] = x[2]
                graph[key] = val
            else:
                val = {x[1]: x[2]}
                graph[key] = val
            continue
        if endstateFlag:
            x = line.split()
            key = x[0]
            val = x[1]
            endstate[key] = val
    return graph, endstate

def find_next_state(graph, token, state, char):
    if state not in graph.keys():
        return None
    for tk in token.keys():
        if char in token[tk]:
            if tk in graph[state].keys():
                return graph[state][tk]
    if "other" in graph[state].keys():
        return graph[state]["other"]
    return None
def check_end_state(end, state):
    if state in end.keys():
        return True
    return False

def output(end, vc_tok, vc_tok_verbose, state, current_word, count_line,count_col):
    print(current_word, file=vc_tok)
    if "\"" in current_word:
        current_word = current_word.replace("\"", "")
        print(f'Kind = {state} [{end[state]}], spelling = \"{current_word}\"'
              f', position = {count_line}({count_col})..{count_line}({count_col + len(current_word) +1})',
              file=vc_tok_verbose)
    else:
        print(f'Kind = {state} [{end[state]}], spelling = \"{current_word}\"'
          f', position = {count_line}({count_col})..{count_line}({count_col + len(current_word) - 1})',
          file=vc_tok_verbose)

def scan(graph, end, token, input_file):
    input_file_path = f"lexer/{input_file}.vc"
    f = open(input_file_path, "r")
    vctok_path = f"lexer/{input_file}.vctok"
    vctok_verbose_path = f"lexer/{input_file}.verbose.vctok"
    vc_tok = open(vctok_path, 'w')
    vc_tok_verbose = open(vctok_verbose_path, 'w')
    state = "0"
    current_word = ""
    count_line = 1
    count_col = 1
    inComment = False
    index_x = -1
    nextFlag = False

    for line in f:
        for x in line:
            index_x += 1

            if nextFlag:
                nextFlag = False
                continue

            #skip comment
            if inComment:
                if "*/" in line:
                    inComment = False
                break
            #next until char non alphabet
            if x.isalpha() and state == "0":
                current_word += x
                if x != line[-1]:
                    continue

            if current_word != "":
                #string literal
                next_state = find_next_state(graph, token, state, x)
                if next_state == "16" or next_state == "17":
                    next_state = find_next_state(graph, token, state, x)
                    if check_end_state(end, next_state):
                        output(end, vc_tok, vc_tok_verbose,next_state, current_word + x, count_line, count_col)
                        count_col = count_col + len(current_word + x)
                        state = "0"
                        current_word = ""
                        continue
                    current_word += x
                    state = next_state
                    continue

                #keyword
                next_state = find_next_state(graph, token, state, current_word)
                if next_state == "3":
                    output(end, vc_tok, vc_tok_verbose, next_state, current_word, count_line, count_col)
                    count_col = count_col + len(current_word) + 1
                    current_word = ""
                    next_state = find_next_state(graph, token, state, x)
                    if end[next_state] == "SPACE":
                        continue
                elif state != "2":
                    state = "1"
            #get 2 consecutive characters
            if index_x < len(line) - 1:
                char_2 = x + line[index_x + 1]
                #skip comment
                if char_2 == '//':
                    current_word = ""
                    break
                elif char_2 == "/*":
                    inComment = True
                    continue

                next_state = find_next_state(graph, token, state, x)
                if next_state == None and check_end_state(end, state):
                    if end[state] != "SPACE":
                        output(end, vc_tok, vc_tok_verbose, state, current_word, count_line, count_col)
                        count_col = count_col + len(current_word)
                        state = "0"
                        current_word = ""

                #input 2 character
                next_state = find_next_state(graph, token, state, char_2)
                if next_state != None:
                    output(end, vc_tok, vc_tok_verbose, next_state, char_2, count_line, count_col)
                    state = "0"
                    count_col += 2
                    nextFlag = True
                    continue

            #check 1 character
            if x not in token["space"]:

                next_state = find_next_state(graph, token, state, x)
                if next_state == None and check_end_state(end, state):
                    if end[state] != "SPACE":
                        output(end, vc_tok, vc_tok_verbose, state, current_word, count_line, count_col)
                    count_col = count_col + len(current_word)
                    current_word = ""
                    state = "0"

                if x == line[-1]:
                    next_state = find_next_state(graph, token, state, x)
                    if check_end_state(end, next_state):
                        if end[next_state] != "SPACE":
                            output(end, vc_tok, vc_tok_verbose, next_state, x, count_line, count_col)

                else:
                    next_state = find_next_state(graph, token, state, x)
                    next_next_state = find_next_state(graph, token, next_state, line[index_x + 1])

                    if next_next_state != None:
                        current_word += x
                        state = next_state
                        continue

                    if check_end_state(end, next_state) and end[next_state] != "SPACE":
                        output(end, vc_tok, vc_tok_verbose, next_state, current_word + x, count_line, count_col)
                        count_col += 1
                        current_word = ""
                        state = "0"

            else:
                count_col = len(current_word) + count_col + 1
                state = "0"
                current_word = ""
                continue

        index_x = -1
        count_line += 1
        count_col = 1

    # add end token
    next_state = find_next_state(graph, token, state, "__eof__")
    output(end, vc_tok, vc_tok_verbose, next_state, "$", count_line, count_col)

def generate_token(file):
    graph, end = readAutomation()
    token = json.load(open('lexer/tokenDefinition.json'))
    scan(graph, end, token, file)
    print("Done")

if __name__ == '__main__':
    generate_token("sample_pscomp")



