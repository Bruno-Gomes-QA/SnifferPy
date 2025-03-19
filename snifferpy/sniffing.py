import sys
import time
import os
import json
import logging
import inspect
import yaml
import psutil

# Configuration file paths
CONFIG_FILE = 'snifferpy.yaml'
CALLS_LOG_FILE = 'snifferpy_calls.json'

# Default settings (merged with snifferpy.yaml)
default_config = {
    'enable': True,  # Enables/disables SnifferPy globally
    'log_level': 'INFO',
    'log_to_file': True,
    'log_filename': 'snifferpy_log.txt',
    'entry_value': False,  # Capture actual argument values? If False, only the type is stored
    'return_value': False,  # Capture actual return values? If False, only the type is stored
    'enable_log': True,  # If False, logging is disabled
    'enable_json': True,  # If False, the JSON report is not generated
    'ignored_modules': [
        'logging',
        'os',
        'threading',
        'builtins',
        'snifferpy',
        'posixpath',
        'genericpath',
    ],  # Default ignored modules
}


class Sniffing:
    def __init__(self):
        # Active function start times and arguments
        self.active_calls = {}
        self.snifferpy_calls = []
        self.config = {}  # Global variable to store loaded configurations

    def __enter__(self):
        self.start_sniffing()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Stops the SnifferPy profiler when exiting the context.

        If an exception occurs inside the `with` block, it will still ensure
        the profiler stops and logs the exception.
        """
        self.stop_sniffing()
        if exc_type is not None:
            logging.error(f'🚨 Unhandled exception detected: {exc_value}')

    def start_sniffing(self):
        """
        Starts the SnifferPy function profiler globally.

        - Loads the configuration from `snifferpy.yaml`.
        - Enables function profiling using `sys.setprofile()`.
        - Ignores functions from modules specified in `ignored_modules`.

        """
        self.load_config()
        if not self.config.get('enable', True):
            logging.warning(
                '⚠️ SnifferPy is disabled in snifferpy.yaml. No functions will be logged.'
            )
            return

        self.setup_logging()
        sys.setprofile(self.profile_function)
        logging.info('🔍 SnifferPy: Global function sniffing started.')

    def stop_sniffing(self):
        """
        Stops function sniffing and saves collected data.

        - Disables function profiling.
        - Saves function call data to `snifferpy_calls.json`, if enabled.
        """
        if not self.config.get('enable', True):
            return

        sys.setprofile(None)
        logging.info('⏹️ SnifferPy: Global function sniffing stopped.')

        if self.config.get('enable_json', True):
            self.save_to_json()
            logging.info(f'📁 Function calls saved to `{CALLS_LOG_FILE}`.')

    def load_config(self):
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
            None: Updates the global [config] dictionary.
        """
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    user_config = yaml.safe_load(f)
                    self.config = {
                        **default_config,
                        **(user_config or {}),
                    }  # Merge default settings with user config

                    # Ensure ignored_modules is always a list
                    if not isinstance(
                        self.config.get('ignored_modules'), list
                    ):
                        self.config['ignored_modules'] = default_config[
                            'ignored_modules'
                        ]

                    return
            except Exception as e:
                print(
                    f'⚠️ Error loading {CONFIG_FILE}: {e}. Using default settings.'
                )

        self.config = default_config  # Use defaults if file does not exist

    def setup_logging(self):
        """
        Configures logging based on [snifferpy.yaml] settings.

        - If `enable_log` is False, logging is skipped.
        - Logs are written to both the terminal and a file if `log_to_file` is enabled.

        """
        if not self.config.get('enable_log', True):  # Skip logging if disabled
            return

        log_level = logging.getLevelName(self.config.get('log_level', 'INFO'))
        log_handlers = [logging.StreamHandler()]  # Always log to terminal

        if self.config.get('log_to_file', True):
            log_filename = self.config.get('log_filename', 'snifferpy_log.txt')
            log_handlers.append(
                logging.FileHandler(log_filename, mode='w')
            )  # Log to file

        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - [%(levelname)s] %(message)s',
            handlers=log_handlers,
        )

    def profile_function(self, frame, event, arg):
        """
        Intercepts and profiles all function calls in the user's code.

        This function ignores functions that belong to:
            - The `ignored_modules` defined in [snifferpy.yaml]
            - Default ignored modules: [logging], [os], `threading`, `builtins`, [snifferpy], `posixpath`, `genericpath`

        The user can add extra modules to ignore, such as `http`, `sqlite3`, etc.

        Args:
            frame (FrameType): The current stack frame.
            event (str): The type of event ([call] or `return`).
            arg (args): The return value of the function (only applicable for `return` events).

        """
        if not self.config.get('enable', True):
            return

        func_name = frame.f_code.co_name

        if event == 'call':
            if self.is_ignored_module(frame):
                return

            args_dict = self.get_args_dict(frame)

            process = psutil.Process(
                os.getpid()
            )  # Reutilizando para melhor desempenho
            start_time = time.perf_counter()
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            cpu_start = process.cpu_times().user + process.cpu_times().system
            mem_start = process.memory_info().rss
            io_start = process.io_counters()
            call_stack = self.get_call_stack()
            called_by = (
                call_stack[-2] if len(call_stack) > 3 else call_stack[-1]
            )

            call_entry = {
                'function': func_name,
                'entry_args': args_dict,
                'return_value': None,
                'execution_time': None,
                'timestamp': timestamp,
                'cpu_usage': None,
                'memory_usage': None,
                'io_operations': None,
                'call_stack': call_stack,
                'called_by': called_by,
                'calls_made': [],
                'success': None,
                'error_message': None,
            }

            self.snifferpy_calls.append(call_entry)
            self.save_to_json()

            self.active_calls[func_name] = {
                'start_time': start_time,
                'args_dict': args_dict,
                'cpu_start': cpu_start,
                'mem_start': mem_start,
                'io_start': io_start,
                'call_stack': call_stack,
                'called_by': called_by,
                'calls_made': [],
                'success': None,
                'error_message': None,
            }

        elif event == 'return':
            if func_name in self.active_calls:
                data = self.active_calls.pop(func_name)

                process = psutil.Process(os.getpid())
                execution_time = time.perf_counter() - data['start_time']
                cpu_end = process.cpu_times().user + process.cpu_times().system
                mem_end = process.memory_info().rss
                io_end = process.io_counters()

                return_value = (
                    arg
                    if self.config.get('return_value', False)
                    else type(arg).__name__
                )

                for call in self.snifferpy_calls:
                    if (
                        call['function'] == func_name
                        and call['execution_time'] is None
                    ):
                        call.update(
                            {
                                'return_value': return_value,
                                'execution_time': execution_time,
                                'cpu_usage': round(
                                    cpu_end - data['cpu_start'], 6
                                ),
                                'memory_usage': f"{(mem_end - data['mem_start']) / (1024 * 1024):.2f}MB",
                                'io_operations': io_end.read_count
                                - data['io_start'].read_count
                                + io_end.write_count
                                - data['io_start'].write_count,
                                'success': True,
                                'error_message': None,
                            }
                        )
                        break

                self.save_to_json()

                if self.config.get('enable_log', True):
                    logging.info(
                        f"📌 Function: {func_name} | Args: {data['args_dict']} | "
                        f'Return: {return_value} | Time: {execution_time:.6f}s | '
                        f"CPU Time: {call['cpu_usage']}s | Memory Used: {call['memory_usage']} | "
                        f"IO Ops: {call['io_operations']} | "
                        f'Success: ✅'
                    )

        elif event == 'exception':
            if func_name in self.active_calls:
                data = self.active_calls.pop(func_name)
                error_message = str(arg)

                for call in self.snifferpy_calls:
                    if (
                        call['function'] == func_name
                        and call['execution_time'] is None
                    ):
                        call.update(
                            {
                                'execution_time': time.perf_counter()
                                - data['start_time'],
                                'cpu_usage': None,
                                'memory_usage': None,
                                'io_operations': None,
                                'success': False,
                                'error_message': error_message,
                            }
                        )
                        break

                self.save_to_json()

                logging.error(
                    f'❌ Function `{func_name}` failed: {error_message}'
                )

    def is_ignored_module(self, frame):
        """
        Checks whether a function belongs to an ignored module.

        This function verifies:
            1. **Module Name ([__name__])** → Avoids capturing calls from [logging], [os], etc.
            2. **File Path ([co_filename])** → Prevents calls from internal files of ignored modules.

        Args:
            frame (FrameType): The current stack frame.

        Returns:
            Ignored (bool): True if the function should be ignored, False otherwise.
        """
        func_module = frame.f_globals.get('__name__', '')
        func_filename = frame.f_code.co_filename

        # Ignore functions from explicitly ignored modules
        if any(
            part in self.config.get('ignored_modules', [])
            for part in func_module.split('.')
        ):
            return True

        return False

    def save_to_json(self):
        """
        Saves the current snifferpy_calls list to the JSON file.

        This ensures that every function call, return, or exception
        is written to the JSON report immediately.
        """
        with open(CALLS_LOG_FILE, 'w') as f:
            json.dump(self.snifferpy_calls, f, indent=4, default=str)

    def get_args_dict(self, frame):
        """Extracts function arguments safely."""
        try:
            args_info = inspect.getargvalues(frame)
            args_dict = {arg: frame.f_locals[arg] for arg in args_info.args}
        except Exception:
            args_dict = 'Unknown (global sniffing)'

        if not self.config.get('entry_value', False):
            args_dict = {
                key: type(value).__name__ for key, value in args_dict.items()
            }

        return args_dict

    @staticmethod
    def get_call_stack():
        """
        Returns a list of function names representing the current call stack.

        This function captures the names of all functions in the current execution stack,
        allowing SnifferPy to track where a function was called from.

        Returns:
            list: List of function names in the current call stack.
        """
        stack = inspect.stack()
        return [
            frame.function for frame in stack[1:]
        ]  # Excludes [get_call_stack] itself
