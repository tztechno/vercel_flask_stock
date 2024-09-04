from flask import Flask, render_template_string
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime

app = Flask(__name__)

# Route for the home page
@app.route('/')
def index():
    symbols_list = sorted(set(['SOXS']))
    d_today = datetime.date.today() + datetime.timedelta(days=1)
    d_start = d_today - datetime.timedelta(days=7*26)
    
    plots = []

    for symbol in symbols_list:
        data = yf.download(symbol, start=d_start, end=d_today, interval="1d")
        data.drop('Volume', axis=1, inplace=True)
        data.columns = [symbol + '_' + f for f in data.columns]
        data.to_csv(symbol + '_series.csv', index=True)
        
        data = pd.read_csv(symbol + '_series.csv')
        data.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'AdjClose']
        data['latest'] = data['Close']
        data['Low min'] = data['Low'].rolling(window=5).min()
        
        fig = make_subplots(specs=[[{"secondary_y": False}]])
        fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name='Close'), secondary_y=False)
        fig.add_trace(go.Scatter(x=data['Date'], y=data['latest'], name='Latest'), secondary_y=False)
        fig.add_trace(go.Scatter(x=data['Date'], y=data['Low min'], name='Low min'), secondary_y=False)
        fig.update_layout(autosize=False, width=700, height=400, title_text=symbol)
        fig.update_xaxes(title_text="Date")
        fig.update_yaxes(title_text=symbol, secondary_y=False)

        # Convert Plotly figure to HTML
        plot_html = fig.to_html(full_html=False)
        plots.append(plot_html)

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Stock Data Visualizations</title>
    </head>
    <body>
        <h1>Stock Data Visualizations</h1>
        {% for plot in plots %}
            <div>{{ plot | safe }}</div>
        {% endfor %}
    </body>
    </html>
    """, plots=plots)

if __name__ == '__main__':
    app.run(debug=True)