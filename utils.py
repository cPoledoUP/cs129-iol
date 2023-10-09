import re

def text_to_token(text: str, tokens: list) -> str:
    current_token = 0
    
    text = re.split("(\s+)", text)
    for i in range(len(text)):
        if text[i].isspace():
            continue
        else:
            text[i] = tokens[current_token][0]
            current_token += 1

    return ''.join(text)