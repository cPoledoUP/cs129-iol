from lexicalanalyzer import *
from utils import *

# testing area
testfile = open('bad.iol')
test = testfile.read()
testfile.close()
tokens = LexicalAnalyzer().tokenize(test)
print(text_to_token(test, tokens[0]))