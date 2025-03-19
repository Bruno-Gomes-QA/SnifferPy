# Getting Started 🚀

## 📌 Overview
**SnifferPy** is a lightweight and powerful Python library for profiling function calls globally. It captures function executions, arguments, return values, execution times, CPU, memory usage, and more, providing a structured JSON report and optional logging.

---

## 🚀 Installation
You can install SnifferPy using pip:
```bash
pip install snifferpy
```

---

## ⚙️ Configuration
SnifferPy uses a `snifferpy.yaml` file for configuration. Here’s an example configuration file:
```yaml
enable: True
log_level: "DEBUG"
log_to_file: True
log_filename: "snifferpy_log.txt"

entry_value: True
return_value: True

enable_log: True
enable_json: True

ignored_modules: ["logging", "os", "threading", "builtins", "snifferpy", "posixpath", "genericpath"]
```
### **Configuration Options:**
| Parameter        | Description |
|----------------|-------------|
| `enable` | Enables or disables SnifferPy globally. |
| `log_level` | Sets the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). |
| `log_to_file` | If `True`, logs will be written to a file. |
| `log_filename` | Name of the log file. |
| `entry_value` | If `True`, logs full argument values instead of just types. |
| `return_value` | If `True`, logs full return values instead of just types. |
| `enable_log` | Enables or disables logging entirely. |
| `enable_json` | Enables or disables JSON report generation. |
| `ignored_modules` | List of modules to ignore when sniffing function calls. |

---

## 🛠️ How to Use SnifferPy
### **1️⃣ Start Sniffing with Context Manager**
SnifferPy now supports an easier and safer way to profile function calls using a context manager:
```python
from snifferpy import Sniffing

with Sniffing():
    def add(a, b):
        return a + b

    def greet(name, age):
        return f"Hello {name}, you are {age} years old!"

    add(3, 7)
    greet("Alice", 25)
```
---

## 📝 Expected Output
### **✅ Log Output (`snifferpy_log.txt`)**
```
2025-03-17 12:00:00 - [INFO] 📌 Function: add | Args: {'a': 3, 'b': 7} | Return: 10 | Time: 0.000001s | CPU: 0.001s | Memory: 1.2MB | IO Ops: 0
2025-03-17 12:00:00 - [INFO] 📌 Function: greet | Args: {'name': 'Alice', 'age': 25} | Return: "Hello Alice, you are 25 years old!" | Time: 0.000002s | CPU: 0.001s | Memory: 1.1MB | IO Ops: 0
```

### **✅ JSON Report (`snifferpy_calls.json`)**
```json
[
    {
        "function": "add",
        "entry_args": {"a": 3, "b": 7},
        "return_value": 10,
        "execution_time": 0.000001,
        "cpu_usage": 0.001,
        "memory_usage": "1.2MB",
        "io_operations": 0,
        "call_stack": ["add", "<module>"],
        "called_by": "<module>",
        "calls_made": []
    },
    {
        "function": "greet",
        "entry_args": {"name": "Alice", "age": 25},
        "return_value": "Hello Alice, you are 25 years old!",
        "execution_time": 0.000002,
        "cpu_usage": 0.001,
        "memory_usage": "1.1MB",
        "io_operations": 0,
        "call_stack": ["greet", "<module>"],
        "called_by": "<module>",
        "calls_made": []
    }
]
```

---

## 📌 Advanced Features
### **🔎 Ignoring Specific Modules**
If you want to exclude specific modules from profiling, modify the `ignored_modules` list in `snifferpy.yaml`. Example:
```yaml
ignored_modules: ["http", "sqlite3"]
```

### **📊 Detailed Execution Reports**
Enable full argument and return values in logs and reports by setting:
```yaml
entry_value: True
return_value: True
```

### **⏸️ Breakpoint Debugging**
SnifferPy will allow setting breakpoints at specific function calls for in-depth debugging.

### **📝 HTML Report Generation**
Generate interactive HTML reports for easier inspection of captured function calls.

### **🔎 Function-Specific Sniffing**
Enable sniffing on specific functions using a decorator:
```python
from snifferpy import sniff

@sniff
def process_data(data):
    return data * 2
```

