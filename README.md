# SnifferPy 🐶

**SnifferPy** is a simple and efficient decorator for tracking function calls, capturing arguments, return values, and execution time. Ideal for debugging and performance analysis in Python.

## 🚀 Installation

To install SnifferPy, use `pip`:

```bash
pip install snifferpy
```

## 🛠️ How to Use SnifferPy
### **1️⃣ Start Sniffing**
To start capturing function calls globally:
```python
from snifferpy import start_sniffing, stop_sniffing

start_sniffing()
```
### **2️⃣ Run Your Code**
```python
def add(a, b):
    return a + b

def greet(name, age):
    return f"Hello {name}, you are {age} years old!"

add(3, 7)
greet("Alice", 25)
```
### **3️⃣ Stop Sniffing and Save the Report**
```python
stop_sniffing()
```
---

## 📜 Expected Output
### **✅ Log Output (`snifferpy_log.txt`)**
```
2025-03-17 12:00:00 - [INFO] 📌 Function: add | Args: {'a': 3, 'b': 7} | Return: 10 | Time: 0.000001s
2025-03-17 12:00:00 - [INFO] 📌 Function: greet | Args: {'name': 'Alice', 'age': 25} | Return: "Hello Alice, you are 25 years old!" | Time: 0.000002s
```

### **✅ JSON Report (`snifferpy_calls.json`)**
```json
[
    {
        "function": "add",
        "entry_args": {"a": 3, "b": 7},
        "return_value": 10,
        "execution_time": 0.000001
    },
    {
        "function": "greet",
        "entry_args": {"name": "Alice", "age": 25},
        "return_value": "Hello Alice, you are 25 years old!",
        "execution_time": 0.000002
    }
]
```

## ⚙️ Configuration (`snifferpy.yml`)

SnifferPy allows configuring its behavior via a `snifferpy.yml` file.

Create this file in your project root and set the desired configurations:

```yaml
enable: True        # Enables/disables tracking globally
log_level: "INFO"          # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
log_to_file: false         # Enables/disables file logging
log_filename: "snifferpy_log.txt"  # Log file name
entry_value: True  # Capture actual argument values
return_value: True  # Capture actual return values
enable_log: True  # Enables or disables logging entirely
enable_json: True  # Enables or disables JSON report generation
ignored_modules: ["logging", "os", "threading", "builtins", "snifferpy", "posixpath", "genericpath"]
```

## 📌 Upcoming Features

- **📄 HTML Report Generation** – Generate an interactive HTML report for easier inspection of captured function calls.
- **⏸️ Breakpoint Debugging** – Allow pausing execution at specific function calls for real-time debugging.
- **🔍 Function-Specific Sniffing** – Enable sniffing only on specific functions using a decorator.

**Keep your code under control with SnifferPy!** 🚀

