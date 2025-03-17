# Getting Started 🚀

## 📌 Overview
**SnifferPy** is a lightweight and powerful Python library for profiling function calls globally. It captures function executions, arguments, return values, and execution times, providing a structured JSON report and optional logging.

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

---

## 📌 Advanced Features
### **🔍 Ignoring Specific Modules**
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

---