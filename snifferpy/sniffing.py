import sys
import time
import os
import json
import logging
import inspect
import yaml
import psutil

# Configuration file paths
CONFIG_FILE = "snifferpy.yaml"
CALLS_LOG_FILE = "snifferpy_calls.json"

# Default settings (merged with snifferpy.yaml)
default_config = {
    "enable": True,  # Enables/disables SnifferPy globally
    "log_level": "INFO",
    "log_to_file": True,
    "log_filename": "snifferpy_log.txt",
    "entry_value": False,  # Capture actual argument values? If False, only the type is stored
    "return_value": False,  # Capture actual return values? If False, only the type is stored
    "enable_log": True,  # If False, logging is disabled
    "enable_json": True,  # If False, the JSON report is not generated
    "ignored_modules": ["logging", "os", "threading", "builtins", "snifferpy", "posixpath", "genericpath"]  # Default ignored modules
}

# Active function start times and arguments
active_calls = {}
snifferpy_calls = []
config = {}  # Global variable to store loaded configurations


def load_config():
    """
    Loads the SnifferPy configuration from `snifferpy.yaml` if available.
    
    This function merges user-defined configurations with default values,
    ensuring that all settings are present.

    The user can customize the modules to ignore by defining `ignored_modules` in the YAML file.

    Example YAML configuration:
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

    Returns:
        None (None): Updates the global `config` dictionary.
    """
    global config
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                user_config = yaml.safe_load(f)
                config = {**default_config, **(user_config or {})}  # Merge default settings with user config
                
                # Ensure ignored_modules is always a list
                if not isinstance(config.get("ignored_modules"), list):
                    config["ignored_modules"] = default_config["ignored_modules"]
                
                return
        except Exception as e:
            print(f"⚠️ Error loading {CONFIG_FILE}: {e}. Using default settings.")
    
    config = default_config  # Use defaults if file does not exist


def setup_logging():
    """
    Configures logging based on `snifferpy.yaml` settings.

    - If `enable_log` is False, logging is skipped.
    - Logs are written to both the terminal and a file if `log_to_file` is enabled.

    """
    if not config.get("enable_log", True):  # Skip logging if disabled
        return

    log_level = logging.getLevelName(config.get("log_level", "INFO"))
    log_handlers = [logging.StreamHandler()]  # Always log to terminal

    if config.get("log_to_file", True):
        log_filename = config.get("log_filename", "snifferpy_log.txt")
        log_handlers.append(logging.FileHandler(log_filename, mode="w"))  # Log to file

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - [%(levelname)s] %(message)s",
        handlers=log_handlers
    )

def is_ignored_module(frame):
    """
    Checks whether a function belongs to an ignored module.

    This function now verifies:
        1. **Module Name (`__name__`)** → Avoids capturing calls from `logging`, `os`, etc.
        2. **File Path (`co_filename`)** → Prevents calls from internal files of ignored modules.

    Args:
        frame (FrameType): The current stack frame.

    Returns:
        Ignored (bool): True if the function should be ignored, False otherwise.
    """
    func_module = frame.f_globals.get("__name__", "")
    func_filename = frame.f_code.co_filename

    # Ignore functions from explicitly ignored modules
    if any(part in config.get("ignored_modules", []) for part in func_module.split(".")):
        return True

    return False

def get_call_stack():
    """
    Returns a list of function names representing the current call stack.

    This function captures the names of all functions in the current execution stack,
    allowing SnifferPy to track where a function was called from.

    Returns:
        list: List of function names in the current call stack.
    """
    stack = inspect.stack()
    return [frame.function for frame in stack[1:]]  # Excludes `get_call_stack` itself

def profile_function(frame, event, arg):
    """
    Intercepts and profiles all function calls in the user's code.

    This function now ignores functions that belong to:
        - The `ignored_modules` defined in `snifferpy.yaml`
        - Default ignored modules: `logging`, `os`, `threading`, `builtins`, `snifferpy`, `posixpath`, `genericpath`

    The user can add extra modules to ignore, such as `http`, `sqlite3`, etc.

    Args:
        frame (FrameType): The current stack frame.
        event (str): The type of event (`call` or `return`).
        arg (args): The return value of the function (only applicable for `return` events).

    """
    if not config.get("enable", True):  # If SnifferPy is disabled, ignore profiling
        return

    func_name = None
    calls_made = []

    if event == "call":
        func_name = frame.f_code.co_name
        func_module = frame.f_globals.get("__name__", "")

        # Ignore functions from modules in the ignored list
        if is_ignored_module(frame):
            return
        
        try:
            args_info = inspect.getargvalues(frame)
            args_dict = {arg: frame.f_locals[arg] for arg in args_info.args}
        except Exception:
            args_dict = "Unknown (global sniffing)"

        if not config.get("entry_value", False):
            args_dict = {key: type(value).__name__ for key, value in args_dict.items()}
        process = psutil.Process(os.getpid())
        start_time = time.perf_counter()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")  
        cpu_start = cpu_start = process.cpu_times().user + process.cpu_times().system
        mem_start = process.memory_info().rss
        io_start = process.io_counters()  
        call_stack = get_call_stack()
        called_by = call_stack[-2] if len(call_stack) > 3 else call_stack[-1]  
        if called_by and called_by in active_calls:
            active_calls[called_by]["calls_made"].append(func_name)

        active_calls[func_name] = {
            "start_time": start_time,
            "args_dict": args_dict,
            "timestamp": timestamp,
            "cpu_start": cpu_start,
            "mem_start": mem_start,
            "io_start": io_start,
            "call_stack": call_stack,
            "called_by": called_by,
            "calls_made": calls_made,
            "success": True,
            "error_message": None
        }

    elif event == "return":
        func_name = frame.f_code.co_name
        if func_name in active_calls:

            data = active_calls[func_name]

            process = psutil.Process(os.getpid())
            start_time, args_dict = data["start_time"], data["args_dict"]
            execution_time = time.perf_counter() - start_time if start_time else 0
            execution_time = time.perf_counter() - data["start_time"]
            cpu_end = process.cpu_times().user + process.cpu_times().system
            mem_end = process.memory_info().rss
            io_end = process.io_counters()

            return_value = arg if config.get("return_value", False) else type(arg).__name__

            call_entry = {
                "function": func_name,
                "entry_args": args_dict,
                "return_value": return_value,
                "execution_time": execution_time,
                "timestamp": data["timestamp"],
                "cpu_usage": round(cpu_end - data["cpu_start"], 6),
                "memory_usage": f"{(mem_end - data['mem_start']) / (1024 * 1024):.2f}MB",
                "io_operations": io_end.read_count - data["io_start"].read_count + io_end.write_count - data["io_start"].write_count,
                "call_stack": data["call_stack"],
                "called_by": data["called_by"],
                "calls_made": data["calls_made"],
                "success": data["success"],
                "error_message": data["error_message"]
            }
            snifferpy_calls.append(call_entry)

            if config.get("enable_log", True):
                logging.info(
                    f"📌 Function: {func_name} | Args: {data['args_dict']} | "
                    f"Return: {return_value} | Time: {execution_time:.6f}s | "
                    f"CPU: {call_entry['cpu_usage']}% | Memory: {call_entry['memory_usage']} | "
                    f"IO Ops: {call_entry['io_operations']}"
                )
    elif event == "exception":
        func_name = frame.f_code.co_name
        if func_name in active_calls:
            active_calls[func_name]["success"] = False
            active_calls[func_name]["error_message"] = str(arg)

            call_entry = {
                "function": func_name,
                "entry_args": active_calls[func_name]["args_dict"],
                "return_value": None,
                "execution_time": time.perf_counter() - active_calls[func_name]["start_time"],
                "timestamp": active_calls[func_name]["timestamp"],
                "cpu_usage": round(psutil.cpu_percent(interval=None) - active_calls[func_name]["cpu_start"], 2),
                "memory_usage": f"{(psutil.Process(os.getpid()).memory_info().rss - active_calls[func_name]['mem_start']) / (1024 * 1024):.2f}MB",
                "io_operations": (
                    psutil.Process(os.getpid()).io_counters().read_count
                    - active_calls[func_name]["io_start"].read_count
                    + psutil.Process(os.getpid()).io_counters().write_count
                    - active_calls[func_name]["io_start"].write_count
                ),
                "call_stack": active_calls[func_name]["call_stack"],
                "called_by": active_calls[func_name]["called_by"],
                "calls_made": active_calls[func_name]["calls_made"],
                "success": False,
                "error_message": active_calls[func_name]["error_message"]
            }

            snifferpy_calls.append(call_entry)
            logging.error(f"❌ Function `{func_name}` failed: {active_calls[func_name]['error_message']}")

            del active_calls[func_name]

def start_sniffing():
    """
    Starts the SnifferPy function profiler globally.

    - Loads the configuration from `snifferpy.yaml`.
    - Enables function profiling using `sys.setprofile()`.
    - Ignores functions from modules specified in `ignored_modules`.

    """
    load_config()
    if not config.get("enable", True):
        logging.warning("⚠️ SnifferPy is disabled in snifferpy.yaml. No functions will be logged.")
        return

    setup_logging()
    sys.setprofile(profile_function)
    logging.info("🔍 SnifferPy: Global function sniffing started.")


def stop_sniffing():
    """
    Stops function sniffing and saves collected data.

    - Disables function profiling.
    - Saves function call data to `snifferpy_calls.json`, if enabled.
    """
    if not config.get("enable", True):
        return

    sys.setprofile(None)
    logging.info("⏹️ SnifferPy: Global function sniffing stopped.")

    if config.get("enable_json", True):
        with open(CALLS_LOG_FILE, "w") as f:
            json.dump(snifferpy_calls, f, indent=4, default=str)
        logging.info(f"📁 Function calls saved to `{CALLS_LOG_FILE}`.")
