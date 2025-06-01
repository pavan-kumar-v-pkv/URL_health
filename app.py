from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
import os
import requests
import logging
import pytz

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Get the absolute path to the data directory
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Use absolute path for SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(DATA_DIR, "url_checks.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class URLCheck(db.Model):
    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False)
    status = Column(String, nullable=False)
    response_time = Column(Float)
    timestamp = Column(DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Kolkata')))

# Initialize database in app context
with app.app_context():
    try:
        logger.info(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        logger.info(f"Checking if database exists: {os.path.exists(os.path.join(DATA_DIR, 'url_checks.db'))}")
        
        # Only create tables if they don't exist
        db.create_all()
        logger.info("Database tables created successfully")
        
        # Only add test entry if there are no existing entries
        if not URLCheck.query.first():
            test_check = URLCheck(url="test", status="TEST", response_time=0)
            db.session.add(test_check)
            db.session.commit()
            logger.info("Test database entry created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise

@app.route('/')
def home():
    # Show the main URL input page
    return render_template('index.html')

@app.route('/history')
def history():
    # Show the history of URL checks
    try:
        checks = URLCheck.query.order_by(URLCheck.timestamp.desc()).all()
        logger.info(f"Fetched {len(checks)} URL checks from database")
        return render_template('history.html', checks=checks)
    except Exception as e:
        logger.error(f"Error fetching history: {str(e)}")
        raise

@app.route('/check_urls', methods=['POST'])
def check_urls():
    try:
        urls = request.form.get('urls', '').strip()
        url_list = [url.strip() for url in urls.split(',') if url.strip()]
        logger.info(f"Received URLs to check: {url_list}")
        
        results = []
        for url in url_list:
            try:
                # Add http:// if not present
                if not url.startswith(('http://', 'https://')):
                    url = 'http://' + url
                
                # Set headers for better compatibility
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
                
                # Handle OpenAI specifically
                if 'openai.com' in url.lower():
                    headers['Accept'] = 'application/json'
                    headers['Content-Type'] = 'application/json'
                    
                # Measure response time
                start_time = datetime.now()
                try:
                    response = requests.get(url, headers=headers, timeout=3)
                    end_time = datetime.now()
                    response_time_ms = (end_time - start_time).total_seconds() * 1000
                    
                    # Check for common API errors
                    if response.status_code == 200:
                        status = 'UP'
                    elif response.status_code in [401, 403]:  # Unauthorized/Forbidden
                        status = 'AUTH_REQUIRED'
                    elif response.status_code == 429:  # Too Many Requests
                        status = 'RATE_LIMITED'
                    else:
                        status = 'DOWN'
                    
                    # Log the status code for debugging
                    logger.info(f"URL: {url}, Status Code: {response.status_code}, Status: {status}, Response Time: {response_time_ms:.1f} ms")
                except requests.exceptions.Timeout:
                    status = 'DOWN'
                    response_time_ms = 3000  # Set to timeout value in milliseconds
                    logger.error(f"Timeout checking URL {url}")
                except Exception as e:
                    status = 'DOWN'
                    response_time_ms = -1
                    logger.error(f"Error checking URL {url}: {str(e)}")
                
                # Save to database
                check = URLCheck(
                    url=url,
                    status=status,
                    response_time=response_time_ms
                )
                db.session.add(check)
                logger.info(f"Added URL check to database: {url} - {status} - {response_time_ms:.1f} ms")
                
                results.append({
                    'url': url,
                    'status': status,
                    'response_time_ms': response_time_ms
                })
            except Exception as e:
                logger.error(f"Error processing URL {url}: {str(e)}")
                continue
        
        # Commit all changes at once after processing all URLs
        db.session.commit()
        logger.info(f"Committed {len(url_list)} URL checks to database")
        
        return render_template('results.html', results=results)
    except Exception as e:
        logger.error(f"Error in check_urls: {str(e)}")
        raise

if __name__ == '__main__':
    # Get port from environment variable, default to 5000
    port = int(os.environ.get('PORT', 5000))
    # Listen on all interfaces
    app.run(host='0.0.0.0', port=port, debug=True)
