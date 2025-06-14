"""
Preprocess data for the TDS Virtual Teaching Assistant

This script processes the discourse_posts.json file and prepares it for
the RAG engine to use.
"""

import json
import os
from pathlib import Path
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def process_discourse_posts():
    """Process discourse posts from JSON file"""
    project_root = Path(__file__).parent.parent
    
    # Path to JSON file
    json_file = project_root / "discourse_posts.json"
    
    # Path to output directory
    output_dir = project_root / "data" / "discourse_posts"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not json_file.exists():
        logger.error(f"Discourse posts JSON file not found at {json_file}")
        return
    
    logger.info(f"Processing discourse posts from {json_file}")
    start_time = time.time()
    
    try:
        # Load JSON data
        with open(json_file, 'r', encoding='utf-8') as f:
            posts = json.load(f)
        
        logger.info(f"Loaded {len(posts)} posts from JSON file")
        
        # Process each post
        processed_count = 0
        for post in posts:
            post_id = post.get('post_id')
            
            if post_id:                # Extract content
                content = post.get('content', '')
                if not content:
                    continue
                
                # Create a markdown file for each post
                output_file = output_dir / f"{post_id}.md"
                
                # Format post data as markdown
                topic_title = post.get('topic_title', '')
                author = post.get('author', '')
                created_at = post.get('created_at', '')
                topic_id = post.get('topic_id', '')
                
                markdown_content = f"""# {topic_title}

**Author:** {author}  
**Date:** {created_at}  
**URL:** https://discourse.onlinedegree.iitm.ac.in/t/{topic_id}/{post_id}

{content}
"""
                
                # Write to file
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                
                processed_count += 1
        
        logger.info(f"Processed {processed_count} posts in {time.time() - start_time:.2f}s")
        
    except Exception as e:
        logger.error(f"Error processing discourse posts: {str(e)}")

if __name__ == "__main__":
    process_discourse_posts()
