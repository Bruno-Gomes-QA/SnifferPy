from snifferpy import start_sniffing, stop_sniffing
import time
# Start sniffing all functions automatically
start_sniffing()

def add(a, b):
    return a + b

def greet(name, age):
    return f"Hello {name}, you are {age} years old!"

add(3, 7)
greet("Alice", 25)

# Stop sniffing and generate reports
stop_sniffing()
