from abc import ABC, abstractmethod

class PropExpression(ABC):
    @abstractmethod
    def run(self) -> bool:
        pass

    @abstractmethod
    def prefix(self) -> str:
        pass

# leaf nodes
class PropTrue(PropExpression):
    def run(self) -> bool:
        return True

    def prefix(self) -> str:
        return "t"

class PropFalse(PropExpression):
    def run(self) -> bool:
        return False

    def prefix(self) -> str:
        return "f"

# internal nodes

class PropAnd(PropExpression):
    def __init__(self, left: PropExpression, right: PropExpression) -> None:
        self.left = left
        self.right = right

    def run(self) -> bool:
        return self.left.run() and self.right.run()

    def prefix(self) -> str:
        return f"and {self.left.prefix()} {self.right.prefix()}"

class PropOr(PropExpression):
    def __init__(self, left: PropExpression, right: PropExpression) -> None:
        self.left = left
        self.right = right

    def run(self) -> bool:
        return self.left.run() or self.right.run()

    def prefix(self) -> str:
        return f"∨ {self.left.prefix()} {self.right.prefix()}"

class PropImply(PropExpression):
    def __init__(self, left: PropExpression, right: PropExpression) -> None:
        self.left = left
        self.right = right

    def run(self) -> bool:
        return not self.left.run() or self.right.run()

    def prefix(self) -> str:
        return f"-> {self.left.prefix()} {self.right.prefix()}"

if __name__ == "__main__":
    # t ∨ f and f  →  t ∨ (f and f)  =  True
    # this is explicitly defined to enforce AND precedence over OR.
    # lexer+parser would be doing it for us in the main app. :)
    expr = PropOr(PropTrue(), PropAnd(PropFalse(), PropFalse()))
    print(expr.run()) ## True
    print(expr.prefix()) ## v t and f f