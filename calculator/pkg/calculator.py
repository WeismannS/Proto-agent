class Calculator:
    def __init__(self):
        self.operators = {
            "+": lambda a, b: a + b,
            "-": lambda a, b: a - b,
            "*": lambda a, b: a * b,
            "/": lambda a, b: a / b,
            "^": lambda a, b: a ** b,
            "%": lambda a, b: a % b
        }

        self.precedence = {
            "+": 1,
            "-": 1,
            "*": 2,
            "/": 2,
            "^": 3,
            "%": 2
        }

    def evaluate(self, expression):
        if not expression:
            return None
        values = []
        operators = []
        tokens = expression.split()

        for token in tokens:
            if token.isdigit():
                values.append(int(token))
            elif token in self.operators:
                while operators and self.precedence[token] <= self.precedence.get(operators[-1], 0):
                    self._apply_op(values, operators.pop())
                operators.append(token)
            elif token == '(':  # Handle parentheses
                operators.append(token)
            elif token == ')':
                while operators and operators[-1] != '(':  # Find matching left parenthesis
                    self._apply_op(values, operators.pop())
                operators.pop()  # Remove left parenthesis
            else:
                raise ValueError("Invalid token: " + token)

        while operators:
            self._apply_op(values, operators.pop())

        return values[0]

    def _apply_op(self, values, op):
        if len(values) < 2:
            raise ValueError("Not enough operands")
        right = values.pop()
        left = values.pop()
        values.append(self.operators[op](left, right))