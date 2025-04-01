import json
import os
import re
from pathlib import Path

def sanitize_filename(title):
    """Convert artifact title to a safe filename"""
    # Replace spaces and special characters with underscores or dashes
    sanitized = re.sub(r'[^\w\s-]', '_', title)
    sanitized = re.sub(r'[\s]+', '_', sanitized)
    return sanitized

def extract_artifacts(json_file_path, output_dir=None):
    """
    Extract artifacts from a Claude conversation JSON file and save them to files
    
    Args:
        json_file_path: Path to the JSON file containing Claude conversation
        output_dir: Directory to save artifacts (default: current directory)
    """
    # Create output directory if specified and doesn't exist
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    else:
        output_dir = "."
    
    # Load the JSON file
    print(f"Loading JSON file: {json_file_path}")
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Initialize counters
    artifacts_found = 0
    artifacts_saved = 0
    
    # Process each message in the conversation
    messages = data.get('chat_messages', [])
    for message in messages:
        # Skip if not assistant message
        if message.get('sender') != 'assistant':
            continue
        # Look for artifacts in the message
        artifacts = []
        
        # Look for function calls that might contain artifacts
        for item in message.get("content"):
            if item.get('type') != 'tool_use' and item.get('name') != 'artifact':
                continue 
            # for function_call in message['function_calls']:
            # if function_call.get('name') == 'artifacts' and function_call.get('parameters'):
            #     params = function_call['parameters']
                
                # For artifact creation
                # if params.get('command') == 'create' and params.get('content') and params.get('title'):
            artifacts_found += 1
            params = item.get('input')
            artifacts.append({
                'title': params.get('title'),
                'content': params.get('content'),
                'language': params.get('language', ''),
                'type': params.get('type', '')
            })
        
        # Save each artifact
        for artifact in artifacts:
            title = artifact['title']
            content = artifact['content']
            artifact_type = artifact['type']
            
            # Determine file extension based on artifact type
            extension = '.txt'  # Default
            if artifact_type == 'application/vnd.ant.code':
                language = artifact['language']
                if language == 'python':
                    extension = '.py'
                elif language == 'javascript':
                    extension = '.js'
                elif language == 'html':
                    extension = '.html'
                elif language == 'css':
                    extension = '.css'
                elif language == 'bash':
                    extension = '.sh'
            elif artifact_type == 'text/markdown':
                extension = '.md'
            elif artifact_type == 'text/html':
                extension = '.html'
            elif artifact_type == 'image/svg+xml':
                extension = '.svg'
            elif artifact_type == 'application/vnd.ant.mermaid':
                extension = '.mmd'
            elif artifact_type == 'application/vnd.ant.react':
                extension = '.jsx'
            
            # Create a safe filename
            print(title)
            if not title:
                continue
            safe_title = sanitize_filename(title)
            filename = f"{safe_title}{extension}"
            filepath = os.path.join(output_dir, filename)
            
            # Save to file
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Saved artifact: {filepath}")
                artifacts_saved += 1
            except Exception as e:
                print(f"Error saving artifact '{title}': {e}")
    
    print(f"\nSummary:")
    print(f"Found {artifacts_found} artifacts")
    print(f"Saved {artifacts_saved} artifacts to {os.path.abspath(output_dir)}")
    
    return artifacts_saved

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract artifacts from Claude conversation JSON')
    parser.add_argument('json_file', help='Path to the Claude conversation JSON file')
    parser.add_argument('--output', '-o', help='Directory to save artifacts (default: current directory)')
    
    args = parser.parse_args()
    
    extract_artifacts(args.json_file, args.output)