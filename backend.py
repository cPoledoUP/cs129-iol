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
    tokens : list
        A list of tokens from last tokenize() call
    errors : list
        A list of errors from last tokenize() call
    var_list : list
        A list of variables from last tokenize() call

    Methods
    ----------
    tokenize(string)
        Converts a given string into a series of tokens and returns whether or not errors were encountered
    word_to_token(word)
        Converts a word into a token
    get_tokens()
        Returns the list of tokens from last tokenize()
    get_var_list()
        Returns the list of variables from last tokenize()
    get_errors()
        Returns the list of errors from last tokenize()
    """

    def __init__(self) -> None:
        self.keywords = ('IOL', 'LOI', 'INT', 'STR', 'IS', 'INTO', 'IS', 'BEG', 'PRINT', 'ADD', 'SUB', 'MULT', 'DIV', 'MOD', 'NEWLN')
        self.tokens = list()
        self.errors = list()
        self.var_list = list()

    def tokenize(self, string: str) -> bool:
        """
        Converts a given string into a series of tokens and returns whether or not errors were encountered

        Parameters
        ----------
        string : str
            An input string to tokenize
        
        Returns
        -------
        bool
            True if no errors encountered, False otherwise
        """

        self.tokens.clear()
        self.errors.clear()
        self.var_list.clear()

        curr_line = 0
        for line in string.splitlines():
            curr_line += 1
            for word in line.split():
                token = self.word_to_token(word)
                self.tokens.append(token)
                if token[0] == 'ERR_LEX':
                    self.errors.append((token[1], curr_line, "unknown word"))
                elif token[0] == 'IDENT':
                    last_token = self.tokens[len(self.tokens) - 2]
                    var_exist = False
                    for var in self.var_list:
                        if token[1] == var[0]:
                            var_exist = True
                            break
                    if last_token[0] == 'STR' or last_token[0] == 'INT':
                        if var_exist:
                            self.errors.append((token[1], curr_line, "duplicate variable definition"))
                        else:
                            self.var_list.append((token[1], last_token[0]))
                    else:
                        if not var_exist:
                            self.errors.append((token[1], curr_line, "undefined variable"))

        
        if len(self.errors) == 0:
            return True
        else:
            return False

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
    
    def get_tokens(self) -> list:
        """
        Returns the list of tokens from last tokenize()
        
        Returns
        -------
        list
            A list of tokens [(token_name, value), ...]
        """
        
        return self.tokens
    
    def get_var_list(self) -> list:
        """
        Returns the list of variables from last tokenize()
        
        Returns
        -------
        list
            A list of variables [(var_name, var_type), ...]
        """
        
        return self.var_list
    
    def get_errors(self) -> list:
        """
        Returns the list of errors from last tokenize()
        
        Returns
        -------
        list
            A list of errors [(error_word, line_number, error_definition), ...]
        """
        
        return self.errors
    
if __name__ == '__main__':
    testfile = open('badvar.iol')
    test = testfile.read()
    testfile.close()
    lex = LexicalAnalyzer()
    
    print(lex.tokenize(test))
    print(lex.get_tokens())
    print(lex.get_var_list())
    print(lex.get_errors())