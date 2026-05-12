"""
SR_PARSER
- from Prof. Dung's lecture notes on PLC

Implementing a simple Shift-Reduce Parser
"""

class SR_Parser:
    def __init__(self):
        self.grammar: list[tuple[str, str]] = []
        self.start_symbol: str | None = None
        self.stack: list[str] = [] # could use stack from Collections also

    def set_grammar(self, file_path):
        self.grammar = list()
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                lhs, rhs = line.split("->")
                self.grammar.append((lhs.strip(), rhs.strip()))
        # assume first line is start symbol
        self.start_symbol = self.grammar[0][0] if self.grammar else None

    def display_grammar(self):
        for lhs, rhs in self.grammar:
            print(f"{lhs} -> {rhs}")

    # shifting operation means we take the leftmost input symbol 
    # from the input string then pushing it onto the stack
    def shift(self, symbol):
        self.stack.append(symbol)
    
    # sample:
    # a => a
    # ad => d, ad
    # adb => b, db, adb
    def _substringify(self, string):
        substrings: list[str] = []
        length = len(string)
        for i in range(length, 0, -1):
            substrings.append(string[i-1:length])
        return substrings

    def _get_possible_reductions(self, stack: list[str]) -> list[tuple[str, str, str]]:
        current_stack_str = ''.join(stack)
        substrings = self._substringify(current_stack_str)

        possible_reductions = []
        for substring in substrings:
            for lhs, rhs in self.grammar:
                if substring == rhs:
                    possible_reductions.append((substring, lhs, rhs))
        return possible_reductions

    def _apply_reduction(self, stack: list[str], lhs: str, rhs: str) -> list[str]:
        new_stack = stack.copy()
        for _ in range(len(rhs)):
            new_stack.pop()
        new_stack.append(lhs)
        return new_stack

    def _reduce_fully(self, stack: list[str], depth: int = 0) -> list[list[str]]:
        indent = "  " * depth
        possible_reductions = self._get_possible_reductions(stack)

        if len(possible_reductions) == 0:
            return [stack]

        if len(possible_reductions) > 1:
            print(f"{indent}Conflict detected! Multiple reductions possible:")
            for i, (_, lhs, rhs) in enumerate(possible_reductions):
                print(f"{indent}  {i+1}. {rhs} -> {lhs}")

        # Try all possible reductions and collect results
        all_results: list[list[str]] = []
        for _, lhs, rhs in possible_reductions:
            print(f"{indent}Trying reduction: {rhs} -> {lhs}")
            new_stack = self._apply_reduction(stack, lhs, rhs)
            print(f"{indent}  Stack after reduction: {''.join(new_stack)}")

            # Recursively reduce the new stack
            results = self._reduce_fully(new_stack, depth + 1)
            all_results.extend(results)

        return all_results

    def parse(self, input_string: str) -> bool:
        return self._parse_recursive(list(input_string), 0, [])

    def _parse_recursive(self, remaining_input: list[str], pos: int, stack: list[str]) -> bool:
        indent = "  " * pos

        # If we've consumed all input, check if we can reduce to start symbol
        if pos >= len(remaining_input):
            # Try all possible reduction paths
            final_stacks = self._reduce_fully(stack, pos)

            for final_stack in final_stacks:
                if len(final_stack) == 1 and final_stack[0] == self.start_symbol:
                    print(f"{indent}SUCCESS! Reduced to start symbol: {self.start_symbol}")
                    return True
            return False

        # Shift the next symbol
        symbol = remaining_input[pos]
        new_stack = stack + [symbol]
        print(f"{indent}Shifted: {symbol} -> Stack: {''.join(new_stack)}")

        # Get all possible reduction paths after this shift
        reduction_results = self._reduce_fully(new_stack, pos)

        # Try continuing from each possible reduction result
        for result_stack in reduction_results:
            print(f"{indent}Continuing with stack: {''.join(result_stack)}")
            if self._parse_recursive(remaining_input, pos + 1, result_stack):
                return True
            print(f"{indent}Backtracking from stack: {''.join(result_stack)}")

        return False


sr_parser = SR_Parser()
sr_parser.set_grammar('./grammar.txt')
sr_parser.display_grammar()

# input string alpha (potentially belonging to L(G))
alpha = "+*nnn"

print(f"\nParsing: {alpha}")
print("=" * 40)

if sr_parser.parse(alpha):
    print("=" * 40)
    print(f"String '{alpha}' is ACCEPTED by the grammar")
else:
    print("=" * 40)
    print(f"String '{alpha}' is REJECTED by the grammar")






