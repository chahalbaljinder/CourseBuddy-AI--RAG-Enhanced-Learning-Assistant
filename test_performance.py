"""
Test script to evaluate the performance of the RAG engine

This script measures the time taken to answer questions and evaluate
the overall performance of the API.
"""

import time
import requests
import statistics
from typing import List, Dict, Any
import json

def wait_for_api_ready(max_retries=10, retry_delay=10):
    """Wait for the API to be fully initialized"""
    health_url = "http://localhost:8000/health"
    
    print("Checking if API is ready...")
    
    for retry in range(max_retries):
        try:
            response = requests.get(health_url)
            
            if response.status_code == 200:
                status_data = response.json()
                
                # Handle both old and new health endpoint formats
                if 'status' in status_data:
                    if status_data.get('status') == 'healthy' or status_data.get('status') == 'ready':
                        print("API is ready for testing!")
                        return True
                    elif status_data.get('status') == 'error':
                        print(f"API initialization error: {status_data.get('error', 'Unknown error')}")
                        return False
                    else:
                        print(f"API is still initializing ({retry+1}/{max_retries}). Waiting {retry_delay} seconds...")
                else:
                    # Old format just returns {"status": "healthy", "timestamp": 123456789}
                    if 'status' in status_data and status_data['status'] == 'healthy':
                        print("API is ready for testing!")
                        return True
            else:
                print(f"Error checking API status: {response.status_code}")
                
        except Exception as e:
            print(f"Error connecting to API: {str(e)}")
            
        if retry < max_retries - 1:
            time.sleep(retry_delay)
    
    print("API did not become ready within the timeout period.")
    return False

def test_api_performance(questions: List[str], num_runs: int = 3) -> Dict[str, Any]:
    """
    Test the performance of the API by sending multiple questions
    and measuring response times.
    
    Args:
        questions: List of questions to test
        num_runs: Number of times to run each question
        
    Returns:
        Dictionary with performance metrics
    """
    url = "http://localhost:8000/"
    results = {
        "questions": [],
        "average_time": 0,
        "min_time": 0,
        "max_time": 0,
        "total_time": 0
    }
    
    all_times = []
    
    for question in questions:
        question_results = {
            "question": question,
            "times": [],
            "average_time": 0,
            "responses": []
        }
        
        for _ in range(num_runs):
            # Send request
            payload = {"question": question}
            start_time = time.time()
            
            try:
                response = requests.post(url, json=payload, timeout=60)
                elapsed_time = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    question_results["times"].append(elapsed_time)
                    question_results["responses"].append(result)
                    all_times.append(elapsed_time)
                    print(f"Question: {question}")
                    print(f"Response time: {elapsed_time:.2f}s")
                    print(f"Answer: {result['answer'][:100]}...")
                    print("-" * 50)
                else:
                    print(f"Error: {response.text}")
            except Exception as e:
                print(f"Error sending request: {str(e)}")
        
        # Calculate average time for this question
        if question_results["times"]:
            question_results["average_time"] = sum(question_results["times"]) / len(question_results["times"])
        
        results["questions"].append(question_results)
    
    # Calculate overall statistics
    if all_times:
        results["average_time"] = sum(all_times) / len(all_times)
        results["min_time"] = min(all_times)
        results["max_time"] = max(all_times)
        results["median_time"] = statistics.median(all_times)
        results["total_time"] = sum(all_times)
    
    return results

def main():
    """Main function to run the performance test"""
    # Check if API is ready first
    if not wait_for_api_ready():
        print("Aborting test as API is not ready.")
        return
    
    # Sample questions
    questions = [
        "Should I use gpt-4o-mini which AI proxy supports, or gpt3.5 turbo?",
        "What is the deadline for GA5?",
        "What is the difference between pandas and numpy?",
        "How do I deploy a Flask app to Heroku?",
        "What is the difference between BERT and GPT?"
    ]
    
    # Run the performance test
    print("Starting performance test...")
    results = test_api_performance(questions, num_runs=1)
    
    # Print overall results
    print("\n" + "=" * 50)
    print("PERFORMANCE RESULTS")
    print("=" * 50)
    print(f"Average response time: {results['average_time']:.2f}s")
    print(f"Minimum response time: {results['min_time']:.2f}s")
    print(f"Maximum response time: {results['max_time']:.2f}s")
    print(f"Median response time: {results['median_time']:.2f}s")
    print(f"Total time: {results['total_time']:.2f}s")
    
    # Save results to file
    with open("performance_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\nResults saved to performance_results.json")

if __name__ == "__main__":
    main()
