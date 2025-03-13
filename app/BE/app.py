from flask import Flask, request, jsonify
from domains_check_MT import check_url_mt
from login import check_login, check_username_avaliability, registration
from DataManagement import (
    load_domains, remove_domain, update_user_task, 
    delete_user_task, load_user_tasks
)
from config import Config, logger
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from elasticapm.contrib.flask import ElasticAPM


app = Flask(__name__)

app.config['ELASTIC_APM'] = {
    'SERVICE_NAME': 'Backend',
    'API_KEY': 'aXhNSi01UUIwZzZuVW5fOWNHc2U6QmRIaDk5XzJTa2VFN1VNbDhrcU9pdw==',
    'SERVER_URL': 'https://my-observability-project-f11779.apm.us-west-2.aws.elastic.cloud:443',
      'ENVIRONMENT': 'local',
}

apm = ElasticAPM(app)

app.config.from_object(Config)

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.start()

"""
Authentication API endpoints
"""

@app.route('/api/login', methods=['POST'])
def login():
    """Handle login requests"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    try:
        if check_login(username, password):
            logger.info(f"Successful login for user: {username}")
            return jsonify({'success': True}), 200
        else:
            logger.warning(f"Failed login attempt for user: {username}")
            return jsonify({'success': False}), 401
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/register', methods=['POST'])
def register():
    """Handle registration requests"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    try:
        Config.ensure_directories()
        registration(username, password)
        logger.info(f"New user registered: {username}")
        return jsonify({'success': True}), 200
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/check-username', methods=['GET'])
def check_username():
    """Check username availability"""
    username = request.args.get('username')
    available = check_username_avaliability(username)
    return jsonify({'available': available})

"""
Domain Management API endpoints
"""

@app.route('/api/domains', methods=['GET'])
def get_domains():
    """Get user domains"""
    username = request.args.get('username')
    try:
        domains = load_domains(username)
        return jsonify(domains)
    except Exception as e:
        logger.error(f"Error loading domains: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/domains', methods=['DELETE'])
def delete_domain():
    """Remove a domain"""
    username = request.args.get('username')
    domain = request.args.get('domain')
    
    try:
        if remove_domain(domain, username):
            logger.info(f"Domain {domain} deleted for user {username}")
            return jsonify({'message': f'Domain {domain} deleted successfully'}), 200
        logger.warning(f"Domain {domain} not found for user {username}")
        return jsonify({'message': 'Domain not found'}), 404
    except Exception as e:
        logger.error(f"Error removing domain: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/check-domains', methods=['POST'])
def check_domains():
    """Check domain status"""
    data = request.get_json()
    try:
        results = check_url_mt(data['domains'], data['username'])
        return jsonify(results)
    except Exception as e:
        logger.error(f"Error checking domains: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
"""
Scheduler API endpoints
"""

@app.route('/api/schedule/hourly', methods=['POST'])
def schedule_hourly():
    """Schedule hourly checks"""
    data = request.get_json()
    username = data.get('username')
    interval = data.get('interval', 1)
    
    try:
        domains = [domain["url"] for domain in load_domains(username)]
        if not domains:
            logger.warning(f"No domains found for user {username}")
            return jsonify({"status": "error", "message": "No domains found"}), 400

        job_id = f"{username}_hourly_task"
        scheduler.add_job(
            func=check_url_mt,
            trigger=IntervalTrigger(hours=interval),
            args=[domains, username],
            id=job_id,
            replace_existing=True
        )
        
        next_run = scheduler.get_job(job_id).next_run_time
        new_task = {
            "type": "hourly",
            "interval": interval,
            "next_run": next_run.strftime("%Y-%m-%dT%H:%M:%S"),
            "job_id": job_id
        }
        update_user_task(username, new_task)
        logger.info(f"Hourly schedule created for user {username}")
        
        return jsonify({
            "status": "success",
            "next_run": next_run.strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        logger.error(f"Scheduler error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/schedule/daily', methods=['POST'])
def schedule_daily():
    """Schedule daily checks"""
    data = request.get_json()
    username = data.get('username')
    time = data.get('time', '00:00')
    hour, minute = map(int, time.split(':'))
    
    try:
        domains = [domain["url"] for domain in load_domains(username)]
        if not domains:
            logger.warning(f"No domains found for user {username}")
            return jsonify({"status": "error", "message": "No domains found"}), 400

        job_id = f"{username}_daily_task"
        scheduler.add_job(
            func=check_url_mt,
            trigger=CronTrigger(hour=hour, minute=minute),
            args=[domains, username],
            id=job_id,
            replace_existing=True
        )
        
        next_run = scheduler.get_job(job_id).next_run_time
        new_task = {
            "type": "daily",
            "time": time,
            "next_run": next_run.strftime("%Y-%m-%dT%H:%M:%S"),
            "job_id": job_id
        }
        update_user_task(username, new_task)
        logger.info(f"Daily schedule created for user {username}")
        
        return jsonify({
            "status": "success",
            "next_run": next_run.strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        logger.error(f"Scheduler error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/schedule/status', methods=['GET'])
def schedule_status():
    """Get schedule status"""
    username = request.args.get('username')
    try:
        tasks = load_user_tasks(username).get("tasks", [])
        return jsonify({
            "status": "success" if tasks else "no task",
            "tasks": tasks
        })
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/schedule/stop', methods=['POST'])
def stop_schedule():
    """Stop scheduled tasks for a user"""
    data = request.get_json()
    username = data.get('username')
    
    if not username:
        return jsonify({
            "status": "error",
            "message": "Username is required"
        }), 400
    
    try:
        # Stop the scheduled job if it exists
        job_id = f"{username}_hourly_task"
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
            
        job_id = f"{username}_daily_task"
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
        
        # Clear the tasks from storage
        delete_user_task(username)
        
        logger.info(f"Stopped scheduler for user: {username}")
        return jsonify({
            "status": "success", 
            "message": "Scheduler stopped for current user"
        })
    except Exception as e:
        logger.error(f"Error stopping scheduler: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    # Ensure all required directories exist
    Config.ensure_directories()
    # Start the application with config values
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)