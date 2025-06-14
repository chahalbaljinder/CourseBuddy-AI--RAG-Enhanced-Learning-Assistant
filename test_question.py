"""
Quick test script for a specific question
"""

import requests
import time

def test_specific_question():
    # API endpoint
    question_url = "http://localhost:8000/"
    question = "Should I use gpt-4o-mini which AI proxy supports, or gpt3.5 turbo?"
    # question = "What is TDS Virtual Teaching Assistant?"
    # question = "Will GA5 not accepting right answers affect my final grade?"
    
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
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error sending request: {str(e)}")

if __name__ == "__main__":
    test_specific_question()
