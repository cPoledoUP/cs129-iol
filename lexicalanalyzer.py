"""
INT_LIT => digit {digit}
digit => 0 | 1 | ... | 9

IDENT => letter {(letter | digit)}
letter => a | b | c | ... | z | A | B | ... | Z
digit => 0 | 1 | ... | 9
"""

class LexicalAnalyzer:
    """
    A class that converts a source file into tokens for the IOL language.

    Token list:
        [KEYWORDS]
        IOL, LOI, INT, STR, IS, INTO, IS, BEG, PRINT, ADD, SUB, MULT, DIV, MOD, NEWLN 
        [OTHER TOKENS]
        ERR_LEX, INT_LIT, IDENT
    
    INT_LIT => digit {digit}
    digit => 0 | 1 | ... | 9

    IDENT => letter {(letter | digit)}
    letter => a | b | c | ... | z | A | B | ... | Z
    digit => 0 | 1 | ... | 9

    Attributes
    ----------
    tba

    Methods
    ----------
    tokenize(src)
        Converts a given 
    """

    def __init__(self) -> None:
        self.keywords = ['IOL', 'LOI', 'INT', 'STR', 'IS', 'INTO', 'IS', 'BEG', 'PRINT', 'ADD', 'SUB', 'MULT', 'DIV', 'MOD', 'NEWLN']

    def tokenize(self, string: str) -> list[list[str]]:
        string_buffer = string.split()
        token_string = list()

        for word in string_buffer:
            token_string.append(self.word_to_token(word))
        
        return token_string

    def word_to_token(self, word : str) -> list[str]:
        # check if word is keyword
        if word in self.keywords:
            return [word, word]
        # check if word is an int_lit or ident or err_lex
        else:
            # Logic:
            # '' --numeric--> 'INT_LIT'
            # '' --alphabet--> 'IDENT'
            # '' --neither--> 'ERR_LEX'
            # 'INT_LIT' --numeric--> 'INT_LIT'
            # 'INT_LIT' --alphabet--> 'ERR_LEX'
            # 'INT_LIT' --neither--> 'ERR_LEX'
            # 'IDENT' --numeric--> 'IDENT'
            # 'IDENT' --alphabet--> 'IDENT'
            # 'IDENT' --neither--> 'ERR_LEX'
            # 'ERR_LEX' --whatever--> 'ERR_LEX'
            possible_token = ''
            for letter in word:
                if possible_token == 'ERR_LEX':
                    return ['ERR_LEX', 'ERR_LEX']
                
                if letter.isnumeric():
                    if possible_token == '' or possible_token == 'INT_LIT':
                        possible_token = 'INT_LIT'
                    elif possible_token == 'IDENT':
                        possible_token = 'IDENT'
                elif letter.isalpha():
                    if possible_token == '' or possible_token == 'IDENT':
                        possible_token = 'IDENT'
                    elif possible_token == 'INT_LIT':
                        possible_token = 'ERR_LEX'
                else:
                    possible_token = 'ERR_LEX'
            
            return [possible_token, word]

# testing area
testfile = open('test.iol')
test = testfile.read()
testfile.close()
print(LexicalAnalyzer().tokenize(test))