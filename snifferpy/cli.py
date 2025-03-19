import subprocess
import os

CONFIG_CONTENT = """\
[server]
headless = true
enableStaticServing = true

[browser]
gatherUsageStats = false
serverAddress = "0.0.0.0"
serverPort = 8501

[client]
toolbarMode = "minimal"
"""


def configure_streamlit():
    """
    Ensures Streamlit is properly configured by creating a `.streamlit/config.toml` file.
    Asks for user confirmation before creating or overwriting the config file.

    Returns:
        bool: True if configuration is set up successfully, False otherwise.
    """
    streamlit_config_path = os.path.join(os.getcwd(), '.streamlit')
    config_file = os.path.join(streamlit_config_path, 'config.toml')

    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                existing_config = f.read().strip()

            if existing_config == CONFIG_CONTENT.strip():
                return True 
        except Exception as e:
            print(f'⚠️ Error reading config file: {e}')

    user_input = (
        input(
            '🔧 SnifferPy needs to configure Streamlit to continue.\n'
            '📁 A local `.streamlit/config.toml` file will be created to avoid unnecessary prompts.\n'
            '❗ This will override any existing configuration in this directory.\n'
            'Do you want to proceed? (Y/n) '
        )
        .strip()
        .lower()
    )

    if user_input and user_input != 'y':
        print(
            '❌ Configuration ignored. To generate the report, the configuration file is required.'
        )
        return False

    os.makedirs(streamlit_config_path, exist_ok=True)

    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(CONFIG_CONTENT)

        print(f'✅ Streamlit configuration saved at {config_file}')
        return True
    except Exception as e:
        print(f'❌ Failed to write config file: {e}')
        return False


def run_report():
    """
    Launches the SnifferPy Streamlit report using the configured settings.
    Ensures the configuration is properly set before running the report.
    """
    if configure_streamlit():
        report_path = os.path.join(os.path.dirname(__file__), 'report.py')
        subprocess.run(['streamlit', 'run', report_path], check=True)


if __name__ == '__main__':
    run_report()
