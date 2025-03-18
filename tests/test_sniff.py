from snifferpy import start_sniffing, stop_sniffing
import time
# Start sniffing all functions automatically
start_sniffing()

def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

def divide(a, b):
    return a / b

def subtract(a, b):
    divide(10, 2)
    add(5, 5)
    return a - b

def greet(name, age):
    add(25, 30)
    subtract(30, 25)
    return f"Hello {name}, you are {age} years old!"

def test_memory_leak():
    for i in range(10):
        add(5, 5)
        multiply(5, 5)
        divide(10, 2)
        subtract(10, 5)
        greet("Alice", 25)
        time.sleep(0.1)

test_memory_leak()
# Stop sniffing and generate reports
stop_sniffing()
