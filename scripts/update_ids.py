"""
Script to update idas incase of changes to the lessons.json file
"""
import json

filename = 'lessons.json'

with open(filename, 'r') as file:
    data = json.load(file)

for index, lesson in enumerate(data['lessons']):
    lesson['id'] = index + 1  # Start from 1

with open(filename, 'w') as file:
    json.dump(data, file, indent=2)
