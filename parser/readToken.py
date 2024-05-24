import re
import json

# read terminate symbol
with open("parser/VCGrammarDefinition.json", 'r') as f:
    data = f.read()
    data = json.loads(data)
    TERMINATE_SYMBOLS = {}
    for key, value in data["decode"].items():
        TERMINATE_SYMBOLS[value] = key

# read token from file .verbose.vctok
def read(file):
    final_data = []
    with open(file, 'r') as f:
        data = f.read()
        data = data.split('\n')
        for x in data:
            if len(re.findall('".*"', x)):

                # token in " "
                token = re.findall('".*"', x)[0].replace('"', '')

                # token in [ ]
                type = re.findall('\[.*\]', x)[0].replace('[', '').replace(']', '')

                # token has form digit(digit)..digit(digit)
                position = re.findall('\d+\(\d+\)\.\.\d+\(\d+\)', x)[0]
                final_data.append({"token": token,
                                   "type": TERMINATE_SYMBOLS[token] if token in TERMINATE_SYMBOLS else type,
                                   "position": position})
    return final_data