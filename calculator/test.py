def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)


def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n - 1)


print("Fibonacci:")
for i in range(1, 11):
    print(f"Fibonacci({i}) = {fibonacci(i)}")

print("\nFactorial:")
for i in range(1, 6):
    print(f"Factorial({i}) = {factorial(i)}")
