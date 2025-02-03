from flask import Flask, render_template, request, session, redirect, jsonify
from flask_session import Session
import requests
from oauthlib.oauth2 import WebApplicationClient
from config import Config, logger

# Initialize Flask application
app = Flask(__name__)
app.config.from_object(Config)
Session(app)

# Initialize OAuth client
client = WebApplicationClient(Config.GOOGLE_CLIENT_ID)

@app.route('/')
def index():
    """Home route"""
    if not session.get("username"):
        return render_template("index.html")
    return render_template('dashboard.html', username=session.get("username"))

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')

@app.route('/<filename>')
def file(filename):
    return app.send_static_file(filename)

@app.route('/login', methods=['POST'])
def login():
    """Handle login"""
    username = request.form.get('username')
    password = request.form.get('password')

    try:
        response = requests.post(f"{Config.BACKEND_URL}/api/login", json={
            'username': username,
            'password': password
        })
        
        if response.status_code == 200:
            session['username'] = username
            logger.info(f"User logged in: {username}")
            return redirect("/")
        else:
            logger.warning(f"Failed login attempt: {username}")
            return render_template("index.html", error_message="Wrong Username or Password")
            
    except requests.exceptions.ConnectionError:
        logger.error("Backend service unavailable")
        return render_template("index.html", error_message="Service temporarily unavailable")
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
        response = requests.post(f"{Config.BACKEND_URL}/api/register", json={
            'username': username,
            'password': password
        })
        
        if response.status_code == 200:
            logger.info(f"New user registered: {username}")
            return render_template("index.html", positive_message="Registration successful. Please sign in.")
        else:
            logger.warning(f"Registration failed: {username}")
            return render_template("registration.html", error_message="Registration failed")
            
    except requests.exceptions.ConnectionError:
        logger.error("Backend service unavailable during registration")
        return render_template("registration.html", error_message="Service temporarily unavailable")
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return render_template("registration.html", error_message="Service temporarily unavailable")

@app.route('/checkUserAvaliability', methods=['GET'])
def check_user_availability():
    """Check username availability"""
    username = request.args.get('username')
    
    try:
        response = requests.get(
            f"{Config.BACKEND_URL}/api/check-username",
            params={'username': username}
        )
        return jsonify(response.json())
    except Exception as e:
        logger.error(f"Username check error: {str(e)}")
        return jsonify({'available': False, 'error': str(e)})

@app.route('/logout')
def logout():
    """Logout route"""
    username = session.get('username')
    if username:
        logger.info(f"User logged out: {username}")
    session.clear()
    return redirect("/")

@app.route("/google-login")
def google_login():
    """Initiate Google login"""
    try:
        google_provider_cfg = requests.get(Config.GOOGLE_DISCOVERY_URL).json()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]
        
        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=Config.CallbackUrl,
            scope=["openid", "email", "profile"]
        )
        return redirect(request_uri)
    except Exception as e:
        logger.error(f"Google login initialization error: {str(e)}")
        return render_template("index.html", error_message="Google login temporarily unavailable")

@app.route("/google-login/callback")
def callback():
    """Handle Google OAuth callback"""
    try:
        code = request.args.get("code")
        google_provider_cfg = requests.get(Config.GOOGLE_DISCOVERY_URL).json()
        token_endpoint = google_provider_cfg["token_endpoint"]
        
        # Get tokens from Google
        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=request.url,
            redirect_url=Config.CallbackUrl,
            code=code,
        )
        
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(Config.GOOGLE_CLIENT_ID, Config.GOOGLE_CLIENT_SECRET),
        )

        client.parse_request_body_response(token_response.text)
        
        # Get user info from Google
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)

        if userinfo_response.json().get("email_verified"):
            users_email = userinfo_response.json()["email"]
            users_name = userinfo_response.json().get("name", "")
            profile_picture = userinfo_response.json().get("picture", "")

            # Register user in backend
            try:
                register_response = requests.post(
                    f"{Config.BACKEND_URL}/api/register",
                    json={
                        'username': users_email,
                        'password': token_response.json()['id_token'],
                        'is_google_user': True
                    }
                )
                
                if register_response.status_code not in [200, 409]:  # 409 would mean user exists
                    raise Exception("Failed to register Google user")
                
                # Set session data
                session["username"] = users_email
                session["full_name"] = users_name
                session["profile_picture"] = profile_picture
                session["is_google_user"] = True
                
                logger.info(f"Google login successful: {users_email}")
                return redirect("/")
                
            except Exception as e:
                logger.error(f"Backend registration error for Google user: {str(e)}")
                return render_template("index.html", error_message="Failed to complete Google login")
        else:
            logger.warning("Google login failed: Email not verified")
            return render_template("index.html", error_message="Email not verified")
            
    except Exception as e:
        logger.error(f"Google login callback error: {str(e)}")
        return render_template("index.html", error_message="Google login failed")

def check_auth():
    """Check if user is authenticated"""
    if not session.get('username'):
        logger.warning("Unauthenticated access attempt")
        return False
    return True

@app.route('/get_domains', methods=['GET'])
def get_domains():
    """Get user's domains"""
    if not check_auth():
        return redirect("/")
        
    try:
        response = requests.get(
            f"{Config.BACKEND_URL}/api/domains",
            params={'username': session['username']}
        )
        return jsonify(response.json())
    except Exception as e:
        logger.error(f"Error getting domains: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/remove_domain', methods=['DELETE'])
def remove_domain():
    """Remove a domain"""
    if not check_auth():
        return redirect("/")
        
    domain = request.args.get('domain')
    if not domain:
        return jsonify({'message': 'No domain provided!'}), 400
        
    try:
        response = requests.delete(
            f"{Config.BACKEND_URL}/api/domains",
            params={'username': session['username'], 'domain': domain}
        )
        return jsonify(response.json())
    except Exception as e:
        logger.error(f"Error removing domain: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/check_domains', methods=['POST'])
def check_domains():
    """Check domains status"""
    if not check_auth():
        return redirect("/")
        
    try:
        data = request.get_json()
        response = requests.post(
            f"{Config.BACKEND_URL}/api/check-domains",
            json={
                'domains': data.get('domains', []), 
                'username': session['username']
            }
        )
        return jsonify(response.json())
    except Exception as e:
        logger.error(f"Domain check error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route("/schedule/hourly", methods=["POST"])
def schedule_hourly():
    """Schedule hourly domain checks"""
    if not check_auth():
        return jsonify({"status": "error", "message": "Not logged in"}), 401

    try:
        response = requests.post(
            f"{Config.BACKEND_URL}/api/schedule/hourly",
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
    if not check_auth():
        return jsonify({"status": "error", "message": "Not logged in"}), 401

    try:
        response = requests.post(
            f"{Config.BACKEND_URL}/api/schedule/daily",
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
    if not check_auth():
        return jsonify({"status": "error", "message": "Not logged in"}), 401

    try:
        response = requests.get(
            f"{Config.BACKEND_URL}/api/schedule/status",
            params={'username': session['username']}
        )
        return jsonify(response.json())
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route("/schedule/stop", methods=["POST"])
def stop_schedule():
    """Stop scheduled tasks"""
    if not check_auth():
        return jsonify({"status": "error", "message": "Not logged in"}), 401

    try:
        response = requests.post(
            f"{Config.BACKEND_URL}/api/schedule/stop",
            json={'username': session['username']}
        )
        return jsonify(response.json())
    except Exception as e:
        logger.error(f"Stop schedule error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)