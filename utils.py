import re

def text_to_token(text: str, tokens: list) -> str:
    """
    Converts a given text into tokenized version while preserving the whitespaces

    Parameters
    ----------
    text : str
        original text
    tokens : list
        list of tokens from the text
    
    Returns
    -------
    str
        the same as original text except the words are replaced with token names
    """
    current_token = 0
    
    text = re.split("(\s+)", text)
    for i in range(len(text)):
        if text[i].isspace():
            continue
        else:
            text[i] = tokens[current_token][0]
            current_token += 1

    return ''.join(text)