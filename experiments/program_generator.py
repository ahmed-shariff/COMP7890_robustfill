import dsl
import random


def generate_program():
    expression_count = random.randint(1, 10)
    expressions = []

    for _ in range(expression_count):
        expressions.append(random.choice(EXPRESSIONS))


if __name__ == "__main__":
    print(dsl.__dir__())
