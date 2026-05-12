from sly import Parser
from components.lexica import PropLogicLexer
from components.ast.prop_logic import PropExpression, PropTrue, PropFalse, PropAnd, PropOr, PropImply

class PropLogicParser(Parser):
    tokens = PropLogicLexer.tokens

    # https://sly.readthedocs.io/en/latest/sly.html#dealing-with-ambiguous-grammars
    precedence = (
        ("left", OR), # left associative, lower precedence
        ("left", AND), # left associative, higher precedence
    )

    @_("expr")
    def statement(self, p) -> PropExpression:
        return p.expr

    @_("expr OR expr")
    def expr(self, p) -> PropExpression:
        return PropOr(p.expr0, p.expr1)

    @_("expr AND expr")
    def expr(self, p) -> PropExpression:
        return PropAnd(p.expr0, p.expr1)

    @_("expr IMPLY expr")
    def expr(self, p) -> PropExpression:
        return PropImply(p.expr0, p.expr1)

    @_("TRUE")
    def expr(self, p) -> PropExpression:
        return PropTrue()

    @_("FALSE")
    def expr(self, p) -> PropExpression:
        return PropFalse()

    # https://sly.readthedocs.io/en/latest/sly.html#panic-mode-recovery
    def error(self, p):
        #discards the entire parsing stack and resets the parser
        self.restart()

        # throw an exception
        if p:
            raise Exception(f"Syntax error at token {p.value} at position {p.index}")
        else:
            raise Exception("Syntax error at EOF")
            
# testing lexer + parser (that utilizes the PropExpression AST)
# here the parser respects the precedence as statically defined
if __name__ == "__main__":
    lexer  = PropLogicLexer()
    parser = PropLogicParser()

    try:
        result = parser.parse(lexer.tokenize("t ∨ f andand  f"))
        print(result.run())    # True
        print(result.prefix()) # ∨ t and f f
    except Exception as e:
        print(e)