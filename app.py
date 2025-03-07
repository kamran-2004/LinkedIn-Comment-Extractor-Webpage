from flask import Flask, render_template, request, send_file, flash
import subprocess
import os
import logging
import sys
import platform
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('linkedin-comment-extractor')

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for flash messages

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        post_url = request.form['post_url']

        logger.info(f"Extraction requested for post: {post_url}")
        logger.info(f"Running on platform: {platform.system()}")
        
        # Run the extraction script
        try:
            logger.info("Starting extraction script...")
            
            # Run the script with output captured
            process = subprocess.Popen(
                ['python', 'script_fixed.py', email, password, post_url],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            # Log the output
            logger.info("Script stdout: " + stdout)
            if stderr:
                logger.error("Script stderr: " + stderr)
                
            if process.returncode != 0:
                raise Exception(f"Script exited with code {process.returncode}: {stderr}")
            
            # Find the latest CSV file
            files = [f for f in os.listdir() if f.startswith('linkedin-comments') and f.endswith('.csv')]
            
            if not files:
                logger.error("No CSV files were generated")
                return render_template('index.html', error="No comments were extracted. The post might not have any comments, or LinkedIn might have blocked the request.")
                
            files.sort(key=os.path.getmtime)
            latest_file = files[-1]
            
            # Check if file is empty or has only header
            file_size = os.path.getsize(latest_file)
            if file_size <= 50:  # Approximate size of just the header row
                logger.warning(f"CSV file is empty or contains only headers: {latest_file} (size: {file_size} bytes)")
                return render_template('index.html', error="No comments were extracted. The post might not have any comments, or LinkedIn might have blocked the request.")
            
            logger.info(f"Serving CSV file: {latest_file} (size: {file_size} bytes)")
            
            # Serve the CSV file for download
            return send_file(latest_file, as_attachment=True)
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            logger.error(error_msg)
            return render_template('index.html', error=error_msg)
            
    return render_template('index.html', render_note="Note: For deployment on Render, make sure Chrome is installed and compatible with the ChromeDriver version.")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = platform.system() == 'Windows'  # Only enable debug mode on Windows for development
    logger.info(f"Starting app on port {port} with debug={debug_mode}")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
