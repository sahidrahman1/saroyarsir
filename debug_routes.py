#!/usr/bin/env python3
"""
Debug route registration
"""
import sys
import os
sys.path.append('/workspaces/saro')

from app import create_app

app = create_app()

def check_routes():
    with app.app_context():
        print("=== All Fee Routes Registered ===")
        for rule in app.url_map.iter_rules():
            if 'fees' in str(rule.rule):
                print(f"{list(rule.methods)} {rule.rule}")
        
        print("\n=== All Routes (first 50) ===")
        count = 0
        for rule in app.url_map.iter_rules():
            if count < 50:
                print(f"{list(rule.methods)} {rule.rule}")
                count += 1

if __name__ == "__main__":
    check_routes()