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
    keywords : tuple
        A list of keywords used by the programming language

    Methods
    ----------
    tokenize(string)
        Converts a given string into a series of tokens and line numbers of possible errors
    word_to_token(word)
        Converts a word into a token
    """

    def __init__(self) -> None:
        self.keywords = ('IOL', 'LOI', 'INT', 'STR', 'IS', 'INTO', 'IS', 'BEG', 'PRINT', 'ADD', 'SUB', 'MULT', 'DIV', 'MOD', 'NEWLN')

    def tokenize(self, string: str) -> list:
        """
        Converts a given string into a series of tokens and line numbers of possible errors

        Parameters
        ----------
        string : str
            An input string to tokenize
        
        Returns
        -------
        list
            The first index contains a list of tokens and the second index contains a list of line numbers where ERR_LEX is found (in order)
        """

        token_string = list()
        error_lines = list()

        curr_line = 0
        for line in string.splitlines():
            curr_line += 1
            for word in line.split():
                token = self.word_to_token(word)
                token_string.append(token)
                if token[0] == 'ERR_LEX':
                    error_lines.append(curr_line)
        
        return [token_string, error_lines]

    def word_to_token(self, word: str) -> tuple:
        """
        Converts a word into a token

        Parameters
        ---------
        word : str
            The word to convert into token
        
        Returns
        -------
        tuple
            A token in the format (TOKEN_NAME, VALUE)
        """

        # check if word is keyword
        if word in self.keywords:
            return (word, word)
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
                    break
                
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
            
            return (possible_token, word)

# testing area
testfile = open('bad.iol')
test = testfile.read()
testfile.close()
print(LexicalAnalyzer().tokenize(test))