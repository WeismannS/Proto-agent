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
            if token.isdigit() or '.' in token:
                values.append(float(token))
            elif token in self.operators:
                while operators and self.precedence[token] <= self.precedence.get(operators[-1], 0):
                    self._apply_op(values, operators.pop())
                operators.append(token)
            elif token == '(':
                operators.append(token)
            elif token == ')':
                while operators and operators[-1] != '(':
                    self._apply_op(values, operators.pop())
                operators.pop()
            else:
                raise ValueError("Invalid token: " + token)

        while operators:
            self._apply_op(values, operators.pop())

        if len(values) != 1:
            raise ValueError("Invalid expression")

        return values[0]

    def _apply_op(self, values, op):
        if len(values) < 2:
            raise ValueError("Not enough operands")
        right = values.pop()
        left = values.pop()
        values.append(self.operators[op](left, right))

if __name__ == "__main__":
    calculator = Calculator()
    expression = "3 + 7 * 2"
    result = calculator.evaluate(expression)
    print(result)
