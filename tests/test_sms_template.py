#!/usr/bin/env python3
"""
Test script to verify SMS template changes (percentage removal)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from routes.monthly_exams import get_default_template, generate_exam_result_message
from datetime import datetime

# Test the default template
default_template = get_default_template('exam_result')
print("Default Template:")
print(default_template)
print()

# Test message generation
class MockStudent:
    def __init__(self):
        self.first_name = "আহমেদ"
        self.full_name = "আহমেদ আলী"

notification = {
    'student': MockStudent(),
    'subject': 'গণিত',
    'marks_obtained': 85,
    'total_marks': 100,
    'percentage': 85.0,
    'grade': 'A',
    'exam_title': 'Monthly Test'
}

message = generate_exam_result_message(default_template, notification)
print("Generated Message:")
print(message)
print(f"Message Length: {len(message)} characters")
print()

# Test fallback for long messages
long_template = "Dear Parent, this is a very long message template that exceeds the SMS character limit of 160 characters. {student_name} scored {marks}/{total} marks in {subject} exam on {date}. Grade: {grade}. This message is intentionally long to test the fallback mechanism."

long_message = generate_exam_result_message(long_template, notification)
print("Long Message Fallback:")
print(long_message)
print(f"Fallback Message Length: {len(long_message)} characters")