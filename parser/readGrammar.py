def readGrammarTable(file_path):
    """

    function reads grammar.dat

    :param file_path: The path of the grammar.dat file does not include the extension

    :return: dict
    { "a" : {"a1" : "val1", "a2" : "val2" , ...}, ... }

    """
    input_file_path = f"parser/{file_path}.dat"
    f = open(input_file_path, "r")

    transitionTable = dict()

    for line in f:
        x = line.split(",")
        key = x[0]
        x[2] = x[2].replace("\n", "")
        key1 = x[1].split(" ")
        x[2] = x[2].split(" ")
        key1.pop(0)
        x[2].pop(0)
        # print(key1)
        for i in key1:
            if key in transitionTable.keys():
                val = transitionTable[key]
                val[i] = x[2]
                transitionTable[key] = val
            else:
                val = {i: x[2]}
                transitionTable[key] = val
    return transitionTable

# test readGrammarTable()
# Go to the folder containing the lexer and parser
# enter "python parser/readGrammar.py" in terminal
if __name__ == '__main__':
    transition = readGrammarTable("grammar")
    count = 0
    for key in transition:
        tmp = str(key) + ", "
        print(key, " :")
        for key1 in transition[key]:
            print("\t", key1, " :", transition[key][key1])