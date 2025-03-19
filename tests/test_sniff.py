from snifferpy import Sniffing
import time


def add(a, b):
    return a + b


def multiply(a, b):
    return a * b


def divide(a, b):
    try:
        return a / b
    except ZeroDivisionError as e:
        raise e


def subtract(a, b):
    divide(10, 2)
    add(5, 5)
    return a - b


def greet(name, age):
    add(25, 30)
    subtract(30, 25)
    return f'Hello {name}, you are {age} years old!'


def test_memory_leak():
    for i in range(10):
        add(5, 5)
        multiply(5, 5)
        subtract(10, 5)
        greet('Alice', 25)
        time.sleep(0.1)


with Sniffing():
    test_memory_leak()
    divide(10, 0)
