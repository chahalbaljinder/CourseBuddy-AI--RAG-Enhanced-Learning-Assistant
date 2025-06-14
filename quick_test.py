"""
Quick test script for the TDS Virtual Teaching Assistant API

This script performs a simple test to check if the API is running
and can answer a basic question.
"""

import requests
import time
import json

def quick_test():
    """Perform a quick test of the API"""
    
    # API endpoint
    health_url = "http://localhost:8000/health"
    
    max_retries = 5
    retry_delay = 5  # seconds
    
    # Check health endpoint with retries
    for retry in range(max_retries):
        try:
            print(f"Checking API health (attempt {retry+1}/{max_retries})...")
            response = requests.get(health_url)
            
            if response.status_code == 200:
                status_data = response.json()
                print(f"API is running! Status: {status_data['status']}")
                
                # If API is not ready, wait and retry
                if status_data['status'] == 'initializing':
                    print(f"API is still initializing. Waiting {retry_delay} seconds before retrying...")
                    time.sleep(retry_delay)
                    continue
                elif status_data['status'] == 'error':
                    print(f"API initialization error: {status_data.get('error', 'Unknown error')}")
                    return
                elif status_data['status'] == 'ready':
                    print("API is ready to answer questions!")
                    break
            else:
                print(f"Error: {response.status_code}")
                print(f"Response: {response.text}")
                time.sleep(retry_delay)
                continue
                
        except Exception as e:
            print(f"Error connecting to API: {str(e)}")
            if retry < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. API may not be running.")
                return
    
    # Test a simple question
    question_url = "http://localhost:8000/"
    question = "What is the deadline for GA5?"
    
    payload = {
        "question": question
    }
    
    try:
        print("\nSending test question...")
        print(f"Question: {question}")
        
        start_time = time.time()
        response = requests.post(question_url, json=payload, timeout=60)
        elapsed_time = time.time() - start_time
        
        print(f"Response time: {elapsed_time:.2f}s")
        
        if response.status_code == 200:
            result = response.json()
            print("\nAnswer:")
            print(result["answer"])
            
            if result["links"]:
                print("\nRelevant links:")
                for link in result["links"]:
                    print(f"- {link['text']}")
                    print(f"  {link['url']}")
            else:
                print("\nNo relevant links found.")
        elif response.status_code == 503:
            print("API is still initializing. Please try again later.")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error sending request: {str(e)}")

if __name__ == "__main__":
    quick_test()
