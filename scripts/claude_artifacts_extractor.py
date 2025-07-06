#!/usr/bin/env python3
import json
import os
import re
import sys
from pathlib import Path

def sanitize_filename(title):
    """Convert artifact title to a safe filename, preserving path separators and removing annotations after extensions"""
    if not title:
        return "unnamed_artifact"
    
    # Common file extensions
    common_extensions = [
        '.py', '.js', '.html', '.css', '.txt', '.md', '.json', '.xml', '.csv', 
        '.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.xls', '.xlsx',
        '.cpp', '.c', '.h', '.java', '.rb', '.php', '.go', '.rs', '.ts', '.jsx',
        '.yml', '.yaml', '.toml', '.ini', '.cfg', '.conf', '.sh', '.bat', '.ps1'
    ]
    
    # Only remove annotations if they follow a common file extension
    for ext in common_extensions:
        pattern = rf'{re.escape(ext)}\s*\([^)]*\)\s*$'
        if re.search(pattern, title, re.IGNORECASE):
            title = re.sub(pattern, ext, title, flags=re.IGNORECASE)
            break
    
    # Handle path separators
    if '/' in title:
        # Split by path separator, sanitize each part, then rejoin
        parts = title.split('/')
        sanitized_parts = []
        for part in parts:
            # Replace spaces and special characters with underscores
            sanitized = re.sub(r'[^\w\s.-]', '_', part)
            sanitized = re.sub(r'[\s]+', '_', sanitized)
            sanitized_parts.append(sanitized)
        return '/'.join(sanitized_parts)
    else:
        # For non-path titles
        sanitized = re.sub(r'[^\w\s.-]', '_', title)
        sanitized = re.sub(r'[\s]+', '_', sanitized)
        return sanitized

def extract_artifacts(json_file_path, output_dir=None):
    """Extract artifacts from a Claude conversation JSON file"""
    # Create output directory if needed
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    else:
        output_dir = "."
    
    # Load the JSON file
    print(f"Loading JSON file: {json_file_path}")
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Could not parse JSON file. {e}")
        return 0
    
    print(f"JSON structure keys: {list(data.keys()) if isinstance(data, dict) else 'not a dictionary'}")
    
    # Find messages based on JSON structure
    messages = []
    if 'chat_messages' in data:
        messages = data['chat_messages']
        print(f"Found {len(messages)} messages in 'chat_messages' structure")
    elif 'messages' in data:
        messages = data['messages']
        print(f"Found {len(messages)} messages in 'messages' structure")
    elif isinstance(data, list):
        messages = data
        print(f"Found {len(messages)} messages in list structure")
    else:
        # Try to find messages nested in the structure
        for key, value in data.items():
            if isinstance(value, dict) and ('messages' in value or 'chat_messages' in value):
                if 'messages' in value:
                    messages = value['messages']
                else:
                    messages = value['chat_messages']
                print(f"Found {len(messages)} messages nested under '{key}'")
                break
    
    if not messages:
        print("No messages found in the JSON structure.")
        return 0
        
    # Debug - print the first message's structure
    if messages and isinstance(messages[0], dict):
        print(f"First message structure: {list(messages[0].keys())}")
    
    # Counters
    artifacts_found = 0
    artifacts_saved = 0
    
    # Process each message
    for message_idx, message in enumerate(messages):
        # Only process assistant messages
        sender = message.get('sender', message.get('role', ''))
        if sender not in ['assistant', 'bot']:
            continue
            
        print(f"Processing assistant message #{message_idx}")
        
        # Initialize artifacts list for this message
        artifacts = []
        
        # Check for different structures where artifacts might be found
        message_content = message.get('content')
        
        # Handle list content (newer Claude format)
        if isinstance(message_content, list):
            for item in message_content:
                if isinstance(item, dict):
                    # Check for tool_use structure
                    if item.get('type') == 'tool_use' and item.get('name') == 'artifacts':
                        print(f"  Found tool_use artifact")
                        params = item.get('input', {})
                        if params and params.get('command') in ['create', 'update'] and (params.get('content')  or params.get('new_str')):
                            artifacts_found += 1
                            artifacts.append({
                                'title': params.get('title', f"artifact_{artifacts_found}"),
                                'content': params.get('content', params.get('new_str')),
                                'language': params.get('language', ''),
                                'type': params.get('type', '')
                            })
                    
                    # Check for function_call structure
                    elif 'function_call' in item:
                        func_call = item.get('function_call', {})
                        if func_call.get('name') == 'artifacts':
                            print(f"  Found function_call artifact")
                            params = func_call.get('parameters', {})
                            if params and params.get('command') == 'create' and params.get('content'):
                                artifacts_found += 1
                                artifacts.append({
                                    'title': params.get('title', f"artifact_{artifacts_found}"),
                                    'content': params.get('content'),
                                    'language': params.get('language', ''),
                                    'type': params.get('type', '')
                                })
        
        # Check for function_calls at the message level
        if 'function_calls' in message:
            for func_call in message.get('function_calls', []):
                if func_call.get('name') == 'artifacts':
                    print(f"  Found message-level function_call artifact")
                    params = func_call.get('parameters', {})
                    if params and params.get('command') == 'create' and params.get('content'):
                        artifacts_found += 1
                        artifacts.append({
                            'title': params.get('title', f"artifact_{artifacts_found}"),
                            'content': params.get('content'),
                            'language': params.get('language', ''),
                            'type': params.get('type', '')
                        })
                        
        # Handle antml:function_calls pattern in text (newer format)
        # This would need to be parsed from text content if present
        
        # Save found artifacts
        for artifact in artifacts:
            title = artifact.get('title', f"artifact_{artifacts_found}")
            content = artifact.get('content', '')
            artifact_type = artifact.get('type', '')
            
            # print(title)
            # Skip empty artifacts
            if not content:
                continue
            
                
            # Determine file extension based on artifact type
            extension = '.txt'  # Default
            if artifact_type == 'application/vnd.ant.code':
                language = artifact.get('language', '')
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
            safe_title = sanitize_filename(title)
            filename = f"{safe_title}"
            
            # Handle path separators in filename
            if '/' in filename:
                dir_path = os.path.join(output_dir, os.path.dirname(filename))
                os.makedirs(dir_path, exist_ok=True)
                
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
    parser.add_argument('json_file', help='Path to the Claude conversation JSON file from eg https://claude.ai/api/organizations/584aa20d-181c-4659-8f8b-44a13429561e/chat_conversations/9dd52f87-f71b-40bd-b858-32f7d935239e?tree=True&rendering_mode=messages&render_all_tools=true')
    # https://claude.ai/api/organizations/584aa20d-181c-4659-8f8b-44a13429561e/chat_conversations/9dd52f87-f71b-40bd-b858-32f7d935239e?tree=True&rendering_mode=messages&render_all_tools=true
    parser.add_argument('--output', '-o', help='Directory to save artifacts (default: current directory)')
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug mode with detailed output')
    
    args = parser.parse_args()
    
    extract_artifacts(args.json_file, args.output)   
