import os
import json
import psycopg2
import modules.DBManagement as DBManagement
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from flask import jsonify
from config import logger, Config


# Make sure the JSON directory exists
def json_directory():
    json_dir = Config.JSON_DIRECTORY
    if not os.path.exists(json_dir):
        os.makedirs(json_dir)
    return json_dir


# Functions to maintain backward compatibility with older code
def load_domains(username):
    """Wrapper for loading domains from database"""
    return DBManagement.load_domains_DB(username)

def update_domains(domains, username):
    """Wrapper for updating domains in database"""
    return DBManagement.update_domains_DB(domains, username)

def remove_domain(domain_to_remove, username):
    """Wrapper for removing a domain from database"""
    return DBManagement.remove_domain_DB(domain_to_remove, username)
    
# schedular data management

def load_user_tasks(username):
    """Load scheduled tasks for a user"""
    try:
        json_dir = json_directory()
        filepath = os.path.join(json_dir, f"{username}_tasks.json")
        if os.path.exists(filepath):
            with open(filepath, "r") as file:
                return json.load(file)
        return {"tasks": []}
    except Exception as e:
        logger.error(f"Error loading tasks for user {username}: {e}")
        return {"tasks": []}

def save_user_tasks(username, tasks):
    """Save the scheduled tasks for a user in a JSON file"""
    try:
        json_dir = json_directory()
        filepath = os.path.join(json_dir, f"{username}_tasks.json")
        with open(filepath, "w") as file:
            json.dump({"tasks": tasks}, file, indent=4)
        logger.debug(f"Saved {len(tasks)} tasks for user {username}")
        return True
    except Exception as e:
        logger.error(f"Error saving tasks for user {username}: {e}")
        return False

def update_user_task(username, new_task):
    """Add or update an existing task for a user"""
    try:
        tasks_data = load_user_tasks(username)
        tasks = tasks_data.get("tasks", [])
        for task in tasks:
            if task["job_id"] == new_task["job_id"]:
                task.update(new_task)
                break
        else:
            tasks.append(new_task)
        save_user_tasks(username, tasks)
        logger.debug(f"Updated task for user {username}: {new_task.get('type')}")
        return True
    
    except Exception as e:
        logger.error(f"Error updating task for user {username}: {e}")
        return False

def delete_user_task(username):
    """Delete all scheduled tasks for a user"""
    try:
        tasks = []
        logger.debug(f"Deleting all tasks for user {username}")
        save_user_tasks(username, tasks)
        return True
    except Exception as e:
        logger.error(f"Error deleting tasks: {e}")
        return False
