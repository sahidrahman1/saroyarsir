#!/usr/bin/env python3
"""
Initialize SMS Balance in Settings
Set the starting balance to 989 SMS
"""

from app import create_app, db
from models import Settings

app = create_app()

def init_sms_balance():
    with app.app_context():
        # Check if balance setting exists
        balance_setting = Settings.query.filter_by(key='sms_balance').first()
        
        if balance_setting:
            print(f"Current SMS balance: {balance_setting.value.get('balance', 0)}")
            response = input("Do you want to update it to 989? (y/n): ")
            if response.lower() == 'y':
                balance_setting.value = {'balance': 989}
                db.session.commit()
                print("✅ SMS balance updated to 989")
            else:
                print("❌ Balance not changed")
        else:
            # Create new balance setting
            balance_setting = Settings(
                key='sms_balance',
                value={'balance': 989},
                category='sms',
                description='Current SMS balance - tracks locally'
            )
            db.session.add(balance_setting)
            db.session.commit()
            print("✅ SMS balance initialized to 989")

if __name__ == "__main__":
    print("SMS Balance Initialization")
    print("=" * 50)
    init_sms_balance()
    print("=" * 50)
    print("Done! Balance is now stored locally in Settings table")
