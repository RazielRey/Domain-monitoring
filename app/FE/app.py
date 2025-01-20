from flask import Flask, render_template, request, session, redirect, jsonify
from flask_session import Session
import os
import requests
from datetime import timedelta
from config import Config, logger
from oauthlib.oauth2 import WebApplicationClient

# Initialize the OAuth client
client = WebApplicationClient(Config.GOOGLE_CLIENT_ID)

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=10)
app.config["SESSION_TYPE"] = "filesystem"
app.config.from_object(Config)
Session(app)


BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5001')


# Home route
@app.route('/')
def index():
    """
    Redirects to the login page if the user is not logged in, otherwise to the dashboard.
    """

    if not session.get("username"):
        return render_template("index.html")
    return render_template('dashboard.html', username=session.get("username"))

# Serve favicon
@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')

# Serve static files
@app.route('/<filename>')
def file(filename):
    return app.send_static_file(filename)

"""
------------------------------
     routes for login
------------------------------

"""

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    try:
        response = requests.post(f"{BACKEND_URL}/api/login", json={
            'username': username,
            'password': password
        })
        
        if response.status_code == 200:
            session['username'] = username
            return redirect("/")
        else:
            return render_template("index.html", error_message="Wrong Username or Password")
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return render_template("index.html", error_message="Service temporarily unavailable")

@app.route('/register')
def register():
    """Registration page route"""
    return render_template('registration.html')

@app.route('/NewUser', methods=['POST'])
def new_user():
    """Handle new user registration"""
    username = request.form.get('username')
    password = request.form.get('password')
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/register", json={
            'username': username,
            'password': password
        })
        
        if response.status_code == 200:
            message = "You have successfully registered. Please sign in."
            return render_template("index.html", positive_message=message)
        else:
            return render_template("registration.html", error_message="Registration failed")
            
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return render_template("registration.html", error_message="Service temporarily unavailable")

@app.route('/checkUserAvaliability', methods=['GET'])
def check_user_availability():
    """Check username availability"""
    username = request.args.get('username')
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/check-username?username={username}")
        return jsonify(response.json())
    except Exception as e:
        logger.error(f"Username check error: {str(e)}")
        return jsonify({'available': False, 'error': str(e)})


@app.route('/logout')
def logout():
    """Logout route"""
    session.clear()
    return redirect("/")



"""
------------------------------
   routes for google login
------------------------------

"""

@app.route("/google-login")
def google_login():
    """Initiate Google login"""
    google_provider_cfg = requests.get(Config.GOOGLE_DISCOVERY_URL).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=Config.CallbackUrl,
        scope=["openid", "email", "profile"]
    )
    return redirect(request_uri)

@app.route("/google-login/callback")
def callback():
    """Handle Google OAuth callback"""
    try:
        code = request.args.get("code")
        # Get Google user info...
        
        # Send to backend for processing
        response = requests.post(f"{BACKEND_URL}/api/google-login", json={
            'email': users_email,
            'name': users_name,
            'google_id': unique_id,
            'profile_picture': profile_picture
        })
        
        if response.status_code == 200:
            data = response.json()
            session["username"] = users_email
            session["full_name"] = users_name
            session["profile_picture"] = profile_picture
            session["is_google_user"] = True
            return redirect("/")
            
    except Exception as e:
        logger.error(f"Google login error: {str(e)}")
        return "Login failed", 400
    

@app.route('/get_domains', methods=['GET'])
def get_domains():
    """Get user's domains"""
    if not session.get('username'):
        return redirect("/")
        
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/domains",
            params={'username': session['username']}
        )
        return jsonify(response.json())
    except Exception as e:
        logger.error(f"Error getting domains: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/remove_domain', methods=['DELETE'])
def remove_domain():
    """Remove a domain"""
    if not session.get('username'):
        return redirect("/")
        
    domain = request.args.get('domain')
    if not domain:
        return jsonify({'message': 'No domain provided!'}), 400
        
    try:
        response = requests.delete(
            f"{BACKEND_URL}/api/domains",
            params={
                'username': session['username'],
                'domain': domain
            }
        )
        return jsonify(response.json())
    except Exception as e:
        logger.error(f"Error removing domain: {str(e)}")
        return jsonify({'error': str(e)}), 500




@app.route('/check_domains', methods=['POST'])
def check_domains():
    if not session.get('username'):
        return redirect("/")
        
    try:
        data = request.get_json()
        response = requests.post(
            f"{BACKEND_URL}/api/check-domains",
            json={'domains': data.get('domains', []), 'username': session['username']}
        )
        return jsonify(response.json())
    except Exception as e:
        logger.error(f"Domain check error: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
# Scheduler routes

"""
------------------------------
    routes for schedular
------------------------------

"""

@app.route("/schedule/hourly", methods=["POST"])
def schedule_hourly():
    """Schedule hourly domain checks"""
    if not session.get("username"):
        return jsonify({"status": "error", "message": "Not logged in"}), 401

    try:
        response = requests.post(
            f"{BACKEND_URL}/api/schedule/hourly",
            json={
                'username': session['username'],
                'interval': request.json.get('interval', 1)
            }
        )
        return jsonify(response.json())
    except Exception as e:
        logger.error(f"Scheduling error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route("/schedule/daily", methods=["POST"])
def schedule_daily():
    """Schedule daily domain checks"""
    if not session.get("username"):
        return jsonify({"status": "error", "message": "Not logged in"}), 401

    try:
        response = requests.post(
            f"{BACKEND_URL}/api/schedule/daily",
            json={
                'username': session['username'],
                'time': request.json.get('time', '00:00')
            }
        )
        return jsonify(response.json())
    except Exception as e:
        logger.error(f"Scheduling error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route("/schedule/status", methods=["GET"])
def schedule_status():
    """Get scheduler status"""
    if not session.get("username"):
        return jsonify({"status": "error", "message": "Not logged in"}), 401

    try:
        response = requests.get(
            f"{BACKEND_URL}/api/schedule/status",
            params={'username': session['username']}
        )
        return jsonify(response.json())
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@app.route("/schedule/stop", methods=["POST"])
def stop_schedule():
    """Stop scheduled tasks"""
    if not session.get("username"):
        return jsonify({"status": "error", "message": "Not logged in"}), 401

    try:
        response = requests.post(
            f"{BACKEND_URL}/api/schedule/stop",
            json={'username': session['username']}
        )
        return jsonify(response.json())
    except Exception as e:
        logger.error(f"Stop schedule error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)