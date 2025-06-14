"""
Demo Test Script with Image Attachment

This script demonstrates how to test the TDS Virtual Teaching Assistant API
with both a question and an image attachment.
"""

import requests
import time
import base64
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import io
import os

def create_test_image(text="GA5 Error: Failed to recognize the correct answer", 
                      file_path="test_image.png", 
                      width=800, 
                      height=400):
    """Create a test image with text for demonstration purposes"""
    # Create a blank image with white background
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Add a border
    draw.rectangle([(0, 0), (width-1, height-1)], outline=(200, 200, 200), width=2)
    
    try:
        # Try to use a system font
        font = ImageFont.truetype("arial.ttf", 24)
    except IOError:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Add text to the image
    draw.text((width//10, height//2), text, fill=(0, 0, 0), font=font)
    
    # Add a title
    draw.rectangle([(0, 0), (width, 50)], fill=(230, 230, 230))
    draw.text((width//10, 15), "TDS Assignment Error", fill=(0, 0, 0), font=font)
    
    # Save the image
    img.save(file_path)
    print(f"Created test image at {file_path}")
    return file_path

def encode_image(image_path):
    """Encode an image file to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def test_with_image():
    """Test the API with both a question and an image"""
    # API endpoint
    question_url = "http://localhost:8000/"
    
    # Create a test question related to the image
    # question = "I'm getting this error in GA5. What should I do to fix it?"
    question = "Should I use gpt-4o-mini which AI proxy supports, or gpt3.5 turbo?"
    
    # Create or use existing test image
    # image_path = "test_image.png"
    image_path = "test_image2.png"
    if not Path(image_path).exists():
        image_path = create_test_image()
    
    # Encode the image
    image_data = encode_image(image_path)
    
    # Prepare the payload
    payload = {
        "question": question,
        "image": image_data
    }
    
    try:
        print("\nSending test question with image...")
        print(f"Question: {question}")
        print(f"Image: {image_path}")
        
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
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error sending request: {str(e)}")

if __name__ == "__main__":
    test_with_image()
