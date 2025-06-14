"""
Test script for the TDS Virtual Teaching Assistant API

This script tests the API by sending a sample question with an image attachment.
"""

import requests
import base64
import json
import os
from pathlib import Path
import time

def test_api():
    """Test the API with a sample question and image"""
    
    # API endpoint
    url = "http://localhost:8000/"
    
    # Sample question
    question = "Should I use gpt-4o-mini which AI proxy supports, or gpt3.5 turbo?"
    
    # Get sample image path
    script_dir = Path(__file__).parent.absolute()
    test_image_path = script_dir / "test_image.png"
    
    # Check if test image exists
    if not test_image_path.exists():
        print(f"Test image not found at {test_image_path}")
        print("Creating a sample test image...")
        
        # Create a simple test image using PIL
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a new image
            img = Image.new('RGB', (800, 400), color=(255, 255, 255))
            draw = ImageDraw.Draw(img)
            
            # Add text
            text = "GA5 Question: Which model should I use for this assignment?"
            draw.text((50, 150), text, fill=(0, 0, 0))
            
            # Save the image
            img.save(test_image_path)
            print(f"Created test image at {test_image_path}")
            
        except ImportError:
            print("PIL not installed. Skipping image attachment.")
            test_image_path = None
    
    # Load and encode image if it exists
    image_data = None
    if test_image_path and test_image_path.exists():
        with open(test_image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode("utf-8")
    
    # Prepare request payload
    payload = {
        "question": question
    }
    
    if image_data:
        payload["image"] = image_data
    
    # Print request information
    print(f"Sending request to {url}")
    print(f"Question: {question}")
    print(f"Image attached: {image_data is not None}")
    
    # Send request
    try:
        start_time = time.time()
        response = requests.post(url, json=payload)
        elapsed_time = time.time() - start_time
        
        # Print response
        print(f"Response time: {elapsed_time:.2f}s")
        print(f"Response status: {response.status_code}")
        
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
    test_api()
