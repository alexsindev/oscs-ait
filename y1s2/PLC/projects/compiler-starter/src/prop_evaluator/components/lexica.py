from sly import Lexer

# We are just piggy-backing off the heavy-lifting lexical analysis 
# work done by Lexer class from sly here. We just need to provide
# the correct definitions 

# Grabbing most implementation stuff from here:
# https://sly.readthedocs.io/en/latest/sly.html#a-more-complete-example
class PropLogicLexer(Lexer):
    # Set of token names.   This is always required
    tokens = {TRUE, FALSE, AND, OR, IMPLY}

    # String containing ignored characters
    # we are ignoring tabs and newline
    ignore = " \t\n"

    # regex for the tokens
    IMPLY = r"->"
    AND   = r"and"
    OR    = r"∨"
    TRUE  = r"t"
    FALSE = r"f"

    # http://sly.readthedocs.io/en/latest/sly.html#error-handling
    def error(self, t):
        print("Illegal character '%s'" % t.value[0])
        self.index += 1

# testing
# running this would return you something like
# Token(type='TRUE', value='t', lineno=1, index=0, end=1)
# Token(type='OR', value='∨', lineno=1, index=2, end=3)
# Token(type='FALSE', value='f', lineno=1, index=4, end=5)
# Token(type='AND', value='and', lineno=1, index=6, end=7)
# Token(type='FALSE', value='f', lineno=1, index=8, end=9)
if __name__ == '__main__':
    data = 't ∨ f and f'
    lexer = PropLogicLexer()
    for tok in lexer.tokenize(data):
        print(tok)