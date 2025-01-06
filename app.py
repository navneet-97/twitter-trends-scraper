# app.py
from flask import Flask, render_template_string # type: ignore
from scraper import scrape_trends
import json

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Twitter Trends Scraper</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .trends { margin: 20px 0; }
        .trend { margin: 10px 0; }
        .json { background-color: #f5f5f5; padding: 20px; border-radius: 5px; }
        pre { white-space: pre-wrap; }
        .error { color: red; }
    </style>
</head>
<body>
    <h1>Twitter Trends Scraper</h1>
    {% if error %}
        <div class="error">{{ error }}</div>
    {% endif %}
    {% if record %}
        <div class="trends">
            <h2>Most happening topics as on {{ record.timestamp.strftime('%Y-%m-%d %H:%M:%S') }}</h2>
            <div class="trend">- {{ record.nameoftrend1 }}</div>
            <div class="trend">- {{ record.nameoftrend2 }}</div>
            <div class="trend">- {{ record.nameoftrend3 }}</div>
            <div class="trend">- {{ record.nameoftrend4 }}</div>
            <div class="trend">- {{ record.nameoftrend5 }}</div>
        </div>
        <p>The IP address used for this query was {{ record.ip_address }}</p>
        <div class="json">
            <h3>MongoDB Record:</h3>
            <pre>{{ json_record }}</pre>
        </div>
    {% endif %}
    <p><a href="{{ url_for('run_scraper') }}">Click here to run the query {% if record %}again{% endif %}</a></p>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/run')
def run_scraper():
    try:
        print("Starting scraping process...")
        record = scrape_trends()
        if record:
            json_record = json.dumps(record, default=str, indent=2)
            return render_template_string(HTML_TEMPLATE, record=record, json_record=json_record)
        else:
            error_message = "Failed to scrape trends. Check the console for detailed logs."
            return render_template_string(HTML_TEMPLATE, error=error_message)
    except Exception as e:
        error_message = f"Error: {str(e)}\nCheck the console for detailed logs."
        return render_template_string(HTML_TEMPLATE, error=error_message)

if __name__ == '__main__':
    app.run(debug=True)