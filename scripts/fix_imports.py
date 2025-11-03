#!/usr/bin/env python3
"""
Fix UserRole imports in all route files
"""
import os
from pathlib import Path

def fix_imports_in_file(file_path):
    """Fix UserRole import in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if UserRole is used but not imported
        if 'UserRole.' in content and 'UserRole' not in content.split('\n')[5]:  # Not in imports section
            lines = content.split('\n')
            
            # Find the import line with models
            for i, line in enumerate(lines):
                if line.startswith('from models import') and 'UserRole' not in line:
                    # Add UserRole to the import
                    if not line.endswith('UserRole'):
                        lines[i] = line.rstrip(', ') + ', UserRole'
                    break
            
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            print(f"✅ Fixed imports in {file_path.name}")
            return True
    
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False
    
    return False

def main():
    """Fix all route files"""
    print("🔧 Fixing UserRole imports in route files...")
    
    routes_dir = Path('routes')
    route_files = list(routes_dir.glob('*.py'))
    
    fixed_count = 0
    for route_file in route_files:
        if fix_imports_in_file(route_file):
            fixed_count += 1
    
    print(f"\n✅ Fixed imports in {fixed_count}/{len(route_files)} files")

if __name__ == '__main__':
    main()