import requests
import time
import os
import json

def register_memorization_task(api_key, user_id, agent_id, conversation):
    base_url = "https://api.memu.so"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "conversation": conversation,
        "user_id": user_id,
        "agent_id": agent_id
    }

    try:
        print(f"Registering task for user: {user_id}, agent: {agent_id}...")
        response = requests.post(
            f"{base_url}/api/v3/memory/memorize",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        result = response.json()
        task_id = result["task_id"]
        print(f"Task registered successfully! Task ID: {task_id}")
        return task_id
    except requests.exceptions.RequestException as e:
        print(f"Error registering task: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response content: {e.response.text}")
        return None

def check_task_status(api_key, task_id):
    base_url = "https://api.memu.so"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print(f"Checking status for task: {task_id}")
    while True:
        try:
            response = requests.get(
                f"{base_url}/api/v3/memory/memorize/status/{task_id}",
                headers=headers
            )
            response.raise_for_status()
            status_data = response.json()
            status = status_data["status"]
            
            print(f"Current status: {status}")
            
            if status == "SUCCESS":
                print("Memorization task completed successfully!")
                return status_data
            elif status == "FAILED":
                print("Memorization task failed!")
                return status_data
            
            time.sleep(5)
        except requests.exceptions.RequestException as e:
            print(f"Error checking status: {e}")
            break

if __name__ == "__main__":
    # Configuration - Replace with your actual values or set environment variables
    API_KEY = os.getenv("MEMU_API_KEY", "YOUR_API_KEY_HERE")
    USER_ID = "user_123"
    AGENT_ID = "agent_456"

    # Sample conversation to memorize
    # Ensure there are at least 3 messages
    CONVERSATION = [
        {"role": "user", "content": "Hi, my name is Alice"},
        {"role": "assistant", "content": "Nice to meet you, Alice!"},
        {"role": "user", "content": "I love hiking and photography. I try to go hiking every weekend."}
    ]

    if API_KEY == "YOUR_API_KEY_HERE":
        print("Please set your MEMU_API_KEY in the script or environment variables.")
    else:
        task_id = register_memorization_task(API_KEY, USER_ID, AGENT_ID, CONVERSATION)
        
        if task_id:
            check_task_status(API_KEY, task_id)
