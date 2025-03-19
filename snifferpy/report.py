import streamlit as st
import json
import os

# Load the JSON report
def load_report():
    report_file = "snifferpy_calls.json"
    if os.path.exists(report_file):
        with open(report_file, "r") as f:
            return json.load(f)
    return []

# Process report data
def process_metrics(report_data):
    total_functions = len(set(call["function"] for call in report_data))
    function_calls = {}
    function_times = {}
    memory_usage = []
    cpu_usage = []
    io_operations = []

    for call in report_data:
        func = call["function"]
        function_calls[func] = function_calls.get(func, 0) + 1
        function_times[func] = max(function_times.get(func, 0), call["execution_time"])
        memory_usage.append(float(call["memory_usage"].replace("MB", "")) if "memory_usage" in call else 0)
        cpu_usage.append(call["cpu_usage"] if "cpu_usage" in call else 0)
        io_operations.append(call["io_operations"] if "io_operations" in call else 0)

    most_called = max(function_calls, key=function_calls.get, default="N/A")
    slowest_function = max(function_times, key=function_times.get, default="N/A")
    avg_memory = sum(memory_usage) / len(memory_usage) if memory_usage else 0
    avg_cpu = sum(cpu_usage) / len(cpu_usage) if cpu_usage else 0
    avg_io = sum(io_operations) / len(io_operations) if io_operations else 0

    return {
        "total_functions": total_functions,
        "slowest_function": (slowest_function, function_times.get(slowest_function, 0)),
        "most_called": (most_called, function_calls.get(most_called, 0)),
        "avg_memory": avg_memory,
        "avg_cpu": avg_cpu,
        "avg_io": avg_io,
    }

# Load report and process metrics
report_data = load_report()
metrics = process_metrics(report_data)

# Streamlit UI
st.set_page_config(page_title="SnifferPy Report", layout="wide")
st.markdown("""
    <style>
        .metric-card {
            padding: 20px;
            border-radius: 10px;
            background-color: #262730;
            text-align: center;
            color: white;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
            margin: 10px 0;
        }
        .metric-title {
            font-size: 18px;
            margin-bottom: 5px;
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #4CAF50;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🐍 SnifferPy Performance Dashboard")

# Layout for the metrics
col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)

def create_card(column, title, value, tooltip, icon):
    column.markdown(f"""
        <div class="metric-card">
            <h5 class="metric-title">
                {icon} {title} 
                <span title='{tooltip}' style="font-size: 12px; vertical-align: top; cursor: help; color: #bbb;">
                    💡
                </span>
            </h5>
            <h3 class="metric-value">{value}</h3>
        </div>
    """, unsafe_allow_html=True)



# First Row
create_card(col1, "Total Functions Monitored", metrics["total_functions"], "Total unique functions tracked in this session.", "📊")
create_card(col2, "Slowest Function", f"{metrics['slowest_function'][0]} - {metrics['slowest_function'][1]:.2f}s", "Function with the highest execution time.", "🐢")
create_card(col3, "Most Called Function", f"{metrics['most_called'][0]} ({metrics['most_called'][1]}x)", "Function that was called the most times.", "🔥")

# Second Row
create_card(col4, "Avg. Memory Usage", f"{metrics['avg_memory']:.2f} MB", "Average memory consumption across all tracked functions.", "💾")
create_card(col5, "Avg. CPU Usage", f"{metrics['avg_cpu']:.6f} sec", "Average CPU time consumed across all tracked functions.", "⚡")
create_card(col6, "Avg. I/O Operations", f"{metrics['avg_io']:.0f}", "Average number of I/O operations performed across all tracked functions.", "🔄")

# Navigation Menu
st.markdown("### 📁 Detailed Reports")
st.write("Select a report to view:")
options = ["Function Details", "Performance Analysis", "I/O Monitoring", "Memory & CPU Usage"]
selected_report = st.selectbox("", options)
st.info("🔍 Use the menu above to explore detailed function performance insights.")
