#!/usr/bin/env python3
"""Check roll numbers in monthly rankings"""

import sqlite3
import os

db_path = '/workspaces/saro/smartgardenhub.db'

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("\n=== CHECKING MONTHLY EXAMS AND ROLL NUMBERS ===\n")

# Get all monthly exams
cursor.execute("""
    SELECT me.id, me.month, me.year, b.name as batch_name
    FROM monthly_exams me
    LEFT JOIN batches b ON me.batch_id = b.id
    ORDER BY me.year DESC, me.month DESC
    LIMIT 5
""")

exams = cursor.fetchall()

if not exams:
    print("No monthly exams found in database!")
    conn.close()
    exit(0)

for exam in exams:
    exam_id, month, year, batch_name = exam
    
    print(f"Exam ID: {exam_id} | {month}/{year} | Batch: {batch_name or 'Unknown'}")
    
    # Get rankings for this exam
    cursor.execute("""
        SELECT 
            mr.id,
            mr.user_id,
            u.first_name || ' ' || u.last_name as student_name,
            mr.roll_number,
            mr.position,
            mr.is_final
        FROM monthly_rankings mr
        LEFT JOIN users u ON mr.user_id = u.id
        WHERE mr.monthly_exam_id = ?
        ORDER BY mr.roll_number
    """, (exam_id,))
    
    rankings = cursor.fetchall()
    
    if rankings:
        print(f"  Total Rankings: {len(rankings)}")
        print(f"\n  Ranking ID | Student Name           | Roll | Position | Saved?")
        print(f"  -----------|------------------------|------|----------|--------")
        
        for r in rankings:
            ranking_id, user_id, student_name, roll_number, position, is_final = r
            roll_str = str(roll_number) if roll_number else 'None'
            saved = 'YES' if is_final else 'NO'
            print(f"  {str(ranking_id).ljust(10)} | {student_name.ljust(22)} | {roll_str.ljust(4)} | {str(position).ljust(8)} | {saved}")
    else:
        print(f"  No rankings found for this exam!\n")
    
    print("\n" + "=" * 80 + "\n")

conn.close()

print("\n💡 IMPORTANT:")
print("- If roll_number shows 'None', rankings haven't been GENERATED yet")
print("- If 'Saved?' shows 'NO', rankings were generated but not finalized")
print("- Click 'Generate Ranking' button to create roll numbers")
print("- Roll numbers inherit from previous month's is_final=TRUE rankings\n")
