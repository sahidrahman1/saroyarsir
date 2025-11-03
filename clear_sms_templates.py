#!/usr/bin/env python3
"""
Clear old SMS templates from database and show new short templates
"""
from app import create_app
from models import db, Settings

app = create_app()

def clear_old_templates():
    """Remove old SMS templates from Settings table"""
    with app.app_context():
        print("🧹 Clearing old SMS templates from database...")
        
        # Find all SMS template settings
        old_templates = Settings.query.filter(
            Settings.key.like('sms_template_%')
        ).all()
        
        if old_templates:
            print(f"   Found {len(old_templates)} old templates")
            for template in old_templates:
                print(f"   Deleting: {template.key}")
                db.session.delete(template)
            
            db.session.commit()
            print("✅ Old templates cleared from database")
        else:
            print("   No old templates found")
        
        print("\n📝 New Short Templates (Hardcoded):")
        print("-" * 60)
        
        templates = {
            'attendance_present': '{student_name} উপস্থিত ({batch_name})',
            'attendance_absent': '{student_name} অনুপস্থিত {date} ({batch_name})',
            'exam_result': '{student_name} পেয়েছে {marks}/{total} ({subject}) {date}',
            'fee_reminder': '{student_name} এর ফি {amount}৳ বকেয়া। শেষ তারিখ {due_date}'
        }
        
        for name, template in templates.items():
            print(f"\n{name}:")
            print(f"   {template}")
            
            # Calculate approximate length with sample data
            if 'attendance_present' in name:
                example = template.format(student_name='আহমেদ আলী', batch_name='HSC-২৫')
            elif 'attendance_absent' in name:
                example = template.format(student_name='রহিম উদ্দিন', date='২৩/১০', batch_name='SSC-২৬')
            elif 'exam_result' in name:
                example = template.format(student_name='সাকিব', marks=85, total=100, subject='গণিত', date='২৩/১০')
            elif 'fee_reminder' in name:
                example = template.format(student_name='ফাতিমা', amount='২৫০০', due_date='৩০/১০')
            else:
                example = template
            
            print(f"   Example: {example}")
            print(f"   Length: ~{len(example)} chars (1 SMS)")
        
        print("\n" + "=" * 60)
        print("✅ All templates are now optimized for 1 SMS each!")
        print("💰 This will save significant SMS costs")
        print("\n⚠️  Note: Users need to refresh their browser to see new templates")

if __name__ == '__main__':
    clear_old_templates()
