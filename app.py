from flask import Flask, render_template, request, send_file
import subprocess
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        post_url = request.form['post_url']

        # Run the extraction script
        try:
            subprocess.run(['python', 'script_fixed.py', email, password, post_url], check=True)
            
            # Find the latest CSV file
            files = [f for f in os.listdir() if f.startswith('linkedin-comments') and f.endswith('.csv')]
            files.sort(key=os.path.getmtime)
            latest_file = files[-1]

            # Serve the CSV file for download
            return send_file(latest_file, as_attachment=True)
        except Exception as e:
            return f"An error occurred: {str(e)}"
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
