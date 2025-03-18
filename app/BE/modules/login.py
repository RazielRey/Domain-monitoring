import json
import os
from config import logger
import modules.DBManagement as DBManagement


def check_login(username, password):
    """function for checking login credentials"""
    logger.debug(f"Checking login for user: {username}")

    try:
        # Check if user exists in the database
        login_success = DBManagement.login_DB(username, password)
       
        if login_success:
            login_type = "regular"
            logger.info(f"Successful {login_type} login for user: {username}")
            return True
        else:
            logger.warning(f"Failed login attempt for user : {username} - Invalid cradentials")
            return False
            
    except Exception as e:
        logger.error(f"Error in check_login: {str(e)}", exc_info=True)
        return False

def check_username_avaliability(username):
    """Check if the username is free before new registration"""
    logger.debug(f"Checking availability for username: {username}")
    try:
        # Check if username exists in the database
        return DBManagement.check_username_DB(username)
    except Exception as e:
        logger.error(f"Error checking username availability: {str(e)}", exc_info=True)
        return False

def registration(username, password, full_name=None, is_google_user=False, profile_picture=None):
    """function for register new username"""
    try:
        # Check if username is available before registration
        username_available = check_username_avaliability(username)
        if username_available:
            NewUser = {
                'username': username.lower(),
                'password': password,
                'full_name': full_name,
                'is_google_user': is_google_user,
                'profile_picture': profile_picture
            }

            # Register new user in the database
            registered = DBManagement.register_DB(NewUser)

            if registered:
                user_type = "Google" if is_google_user else "regular"
                logger.info(f"New {user_type} user registered: {username}")
                return True
            else:
                logger.error(f"Error registering new user: {username}")
                return False
        else:
            # If username exists and it's a Google login attempt, just log it
            if is_google_user:
                logger.info (f"Existing Google user login attempt: {username}")
                return True
            else:
                logger.info(f"Username already exists: {username}")
                return False
    except Exception as e:
        logger.error(f"Error during registration: {str(e)}", exc_info=True)
        raise