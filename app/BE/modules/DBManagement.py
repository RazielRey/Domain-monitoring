import psycopg2
from config import logger, Config
import os

# Database connection parameters
DB_PARAMS = {
    'dbname': os.getenv('DB_NAME', 'monidb'),
    'user': os.getenv('DB_USER', 'myuser'),
    'password': os.getenv('DB_PASSWORD', 'mypassword'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '5432'))
}
logger.error(f"DB Params in use at startup: {DB_PARAMS}")
# Function to connect to the database
def connect_db():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise

# Function to connect to the database
def connect_db():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise

def register_DB(newuser):
    """
    Register a new user in the database
    
    Args:
        newuser (dict): User details (username, password, full_name, is_google_user, profile_picture)
    
    Returns:
        bool: Success status
    """
    try:
        logger.info(f"DB Params in use: {DB_PARAMS}")
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('INSERT INTO users (username, password, full_name, is_google_user, profile_picture) VALUES (%s, %s, %s, %s, %s)', 
                   (newuser["username"], newuser["password"], newuser["full_name"], 
                    newuser["is_google_user"], newuser["profile_picture"]))
               
        conn.commit()
        # Check rowcount to verify success
        if cur.rowcount > 0:
            logger.info(f"User {newuser['username']} added successfully")
            return True
        else:
            logger.error(f"Error adding user {newuser['username']}")
            return False
            
    except Exception as e:
        logger.error(f"Database error in register_DB: {e}")
        return False
    finally:
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn:
            conn.close()

def login_DB(username, password):
    """
    Verify user login credentials
    
    Args:
        username (str): Username to check
        password (str): Password to verify
    
    Returns:
        bool: True if login is valid, False otherwise
    """
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        true_login = cur.fetchone()
        return true_login is not None
    except Exception as e:
        logger.error(f"Database error in login_DB: {e}")
        return False
    finally:    
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn:
            conn.close()    

def check_username_DB(username):
    """
    Check if a username is available for registration
    
    Args:
        username (str): Username to check
    
    Returns:
        bool: True if username is available, False if already exists
    """
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE username = %s', (username,))
        username_exists = cur.fetchone()
        return username_exists is None
    except Exception as e:  
        logger.error(f"Database error in check_username_DB: {e}")
        return False
    finally:
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn:
            conn.close()

def load_domains_DB(username):
    """
    Load domains and their status for a user
    
    Args:
        username (str): Username to get domains for
    
    Returns:
        list: List of domain dictionaries with their status
    """
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('''
                    SELECT s.url, s.status_code, s.ssl_status, s.expiration_date, s.issuer
                    FROM scans s 
                    JOIN users u ON s.user_id = u.user_id
                    WHERE u.username = %s''', (username,))
        results = cur.fetchall()
        domains = []
        if results:
            for result in results:
                domains.append({
                    'url': result[0],
                    'status_code': result[1],
                    'ssl_status': result[2],
                    'expiration_date': result[3],
                    'issuer': result[4]
                })
            logger.debug(f"Loaded {len(domains)} domains for user {username}")
            return domains
        else:
            logger.debug(f"No domains found for user {username}")
            return []
    except Exception as e:
        logger.error(f"Error loading domains: {e}")
        return []
    finally:
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn:
            conn.close()

def update_domains_DB(domains, username):
    """
    Update domain status in database
    
    Args:
        domains (list): List of domain dictionaries with status information
        username (str): Username who owns the domains
    
    Returns:
        bool: Success status
    """
    try:
        conn = connect_db()
        cur = conn.cursor()
        for domain in domains:
            cur.execute('''
                        INSERT INTO scans (url, status_code, ssl_status, expiration_date, issuer, user_id)
                        VALUES (%s, %s, %s, %s, %s, (SELECT user_id FROM users WHERE username = %s))
                        ON CONFLICT (user_id, url) DO UPDATE
                        SET status_code = EXCLUDED.status_code,
                            ssl_status = EXCLUDED.ssl_status,
                            expiration_date = EXCLUDED.expiration_date,
                            issuer = EXCLUDED.issuer,
                            last_scan_time = CURRENT_TIMESTAMP
                        ''', (domain['url'], domain['status_code'], domain['ssl_status'], 
                              domain['expiration_date'], domain['issuer'], username))
        
        conn.commit()
        logger.debug(f"Updated {len(domains)} domains for user {username}")
        return True
    except Exception as e:  
        logger.error(f"Error updating domains: {e}")
        conn.rollback()
        return False
    finally:
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn:
            conn.close()    

def remove_domain_DB(domain_to_remove, username):
    """
    Remove a domain from monitoring
    
    Args:
        domain_to_remove (str): Domain URL to remove
        username (str): Username who owns the domain
    
    Returns:
        bool: Success status
    """
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('''
                    DELETE FROM scans
                    WHERE url = %s AND user_id = (SELECT user_id FROM users WHERE username = %s)
                    RETURNING url
                    ''', (domain_to_remove, username))
        result = cur.fetchone()
        conn.commit()
        if result:
            logger.debug(f"Domain {domain_to_remove} removed for user {username}")
            return True
        else:
            logger.debug(f"Domain {domain_to_remove} not found for user {username}")
            return False
    except Exception as e:
        logger.error(f"Error removing domain: {e}")
        conn.rollback()
        return False
    finally:    
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn:
            conn.close()