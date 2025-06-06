from flask import Flask, render_template_string, request, send_file
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
import os

app = Flask(__name__)

class FuncParse():
    def __init__(self, func=None):
        self.func = func 

    @property
    def func(self):
        return self._func

    @func.setter
    def func(self, func):
        if not isinstance(func, str) or not func.strip():
            raise ValueError("Function must be a non-empty string.")
        try:
            sp.sympify(func)
        except (sp.SympifyError, TypeError):
            raise ValueError("Invalid SymPy expression. Use standard SymPy syntax.")
        self._func = func

    def parse(self):
        self.parsed_func = sp.sympify(self._func)
        return self.parsed_func

def f_web(func, h, n):
    try:
        h = float(h)
        n = int(n)
    except ValueError:
        return "Please enter valid numeric values for interval and number."

    try:
        func_parse = FuncParse(func)
        parsed_func = func_parse.parse()
    except ValueError as e:
        return str(e)

    t = np.linspace(0, h*n, 1000)
    output = np.zeros_like(t)

    t_symbol = sp.symbols('t')
    eval_func = sp.lambdify(t_symbol, parsed_func, 'numpy')

    for i in range(n+1):
        shifted_t = t - i*h
        heavi = shifted_t >= 0

        for idx, t_val in enumerate(shifted_t):
            if heavi[idx]:
                output[idx] += eval_func(t_val)

    plt.figure()
    plt.plot(t, output)
    plt.xlabel('Time (t)')
    plt.ylabel('Function Value')
    plt.title('Function Value vs Time')
    plt.grid(True)
    plt.savefig("plot.png")
    plt.close()

    return None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Periodic Step-Function GC</title>
    <style>
        body {
            background-color: #fff8dc;
            font-family: "Times New Roman", Times, serif;
            padding: 20px;
        }
        .input-section, .plot-section {
            margin-bottom: 20px;
        }
        .plot-section {
            border: 2px solid #444;
            padding: 15px;
            background-color: #ffffff;
            margin-top: 20px;
            font-family: monospace;
            max-height: 500px;
            overflow-y: auto;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.2);
        }
        .plot-section img {
            max-width: 100%;
            height: auto;
        }
        .label {
            font-weight: bold;
        }
        .error {
            color: red;
        }
    </style>
</head>
<body>
    <h2>Periodic Step-Function Grapher</h2>
    <form method="post">
        <div class="input-section">
            <label class="label">Function (in variable t, use SymPy syntax):</label><br>
            <input type="text" name="function" required value="{{ func }}"><br><br>

            <label class="label">Time Gap between repetitions:</label><br>
            <input type="text" name="time_interval" required value="{{ time_interval }}"><br><br>

            <label class="label">Number of repetitions:</label><br>
            <input type="text" name="num_intervals" required value="{{ num_intervals }}"><br><br>

            <input type="submit" value="Plot">
        </div>
    </form>

    <div class="plot-section">
        {% if plot_ready %}
        <h3>Graph Output:</h3>
        <img src="/plot.png" alt="Plot">
        {% elif error %}
        <p class="error">{{ error }}</p>
        {% else %}
        <p>Submit a function to generate the plot.</p>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def web_interface():
    plot_ready = False
    error = None

    func = request.form.get("function", "")
    time_interval = request.form.get("time_interval", "")
    num_intervals = request.form.get("num_intervals", "")

    if request.method == "POST":
        error = f_web(func, time_interval, num_intervals)
        if not error:
            plot_ready = True

    return render_template_string(HTML_TEMPLATE, plot_ready=plot_ready, error=error,
                                  func=func, time_interval=time_interval, num_intervals=num_intervals)

@app.route("/plot.png")
def serve_plot():
    return send_file("plot.png", mimetype='image/png')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
