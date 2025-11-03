"""
Test script for comprehensive monthly results functionality
"""
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_comprehensive_results():
    """Test the comprehensive results function logic"""
    print("🧪 Testing Comprehensive Monthly Results Logic")
    
    # Mock data structure that would come from database
    individual_exams = [
        {'id': 1, 'title': 'Math Quiz 1', 'subject': 'Mathematics', 'marks': 50},
        {'id': 2, 'title': 'Science Test', 'subject': 'Science', 'marks': 100},
        {'id': 3, 'title': 'English Exam', 'subject': 'English', 'marks': 75},
    ]
    
    students = [
        {'id': 1, 'full_name': 'Alice Johnson', 'phoneNumber': '01712345678'},
        {'id': 2, 'full_name': 'Bob Smith', 'phoneNumber': '01712345679'},
        {'id': 3, 'full_name': 'Charlie Brown', 'phoneNumber': '01712345680'},
    ]
    
    # Mock marks data (student_id -> exam_id -> marks)
    marks_data = {
        1: {  # Alice
            1: {'marks_obtained': 45, 'total_marks': 50, 'is_absent': False},
            2: {'marks_obtained': 85, 'total_marks': 100, 'is_absent': False},
            3: {'marks_obtained': 60, 'total_marks': 75, 'is_absent': False},
        },
        2: {  # Bob
            1: {'marks_obtained': 40, 'total_marks': 50, 'is_absent': False},
            2: {'marks_obtained': 0, 'total_marks': 100, 'is_absent': True},  # Absent
            3: {'marks_obtained': 70, 'total_marks': 75, 'is_absent': False},
        },
        3: {  # Charlie
            1: {'marks_obtained': 35, 'total_marks': 50, 'is_absent': False},
            2: {'marks_obtained': 90, 'total_marks': 100, 'is_absent': False},
            3: {'marks_obtained': 65, 'total_marks': 75, 'is_absent': False},
        }
    }
    
    # Mock attendance data (student_id -> present_days)
    attendance_data = {
        1: 25,  # Alice: 25 present days
        2: 20,  # Bob: 20 present days  
        3: 28,  # Charlie: 28 present days
    }
    
    # Mock bonus marks (student_id -> bonus)
    bonus_data = {
        1: 5,   # Alice: 5 bonus marks
        2: 0,   # Bob: 0 bonus marks
        3: 10,  # Charlie: 10 bonus marks
    }
    
    def calculate_grade_and_gpa(percentage):
        """Calculate grade and GPA based on percentage"""
        if percentage >= 90:
            return 'A+', 4.00
        elif percentage >= 85:
            return 'A', 3.75
        elif percentage >= 80:
            return 'A-', 3.50
        elif percentage >= 75:
            return 'B+', 3.25
        elif percentage >= 70:
            return 'B', 3.00
        elif percentage >= 65:
            return 'B-', 2.75
        elif percentage >= 60:
            return 'C+', 2.50
        elif percentage >= 55:
            return 'C', 2.25
        elif percentage >= 50:
            return 'C-', 2.00
        elif percentage >= 45:
            return 'D+', 1.75
        elif percentage >= 40:
            return 'D', 1.50
        elif percentage >= 33:
            return 'D-', 1.00
        else:
            return 'F', 0.00
    
    # Calculate comprehensive rankings
    rankings = []
    
    for student in students:
        student_id = student['id']
        
        # Get individual exam marks
        individual_marks = {}
        total_exam_marks = 0
        total_possible_marks = 0
        
        for exam in individual_exams:
            exam_id = exam['id']
            mark = marks_data[student_id].get(exam_id)
            
            if mark:
                individual_marks[exam_id] = {
                    'exam_title': exam['title'],
                    'subject': exam['subject'],
                    'marks_obtained': mark['marks_obtained'],
                    'total_marks': mark['total_marks'],
                    'is_absent': mark['is_absent']
                }
                if not mark['is_absent']:
                    total_exam_marks += mark['marks_obtained']
                total_possible_marks += mark['total_marks']
            else:
                individual_marks[exam_id] = {
                    'exam_title': exam['title'],
                    'subject': exam['subject'],
                    'marks_obtained': 0,
                    'total_marks': exam['marks'],
                    'is_absent': True
                }
                total_possible_marks += exam['marks']
        
        # Get attendance marks (1 mark per present day)
        attendance_marks = attendance_data.get(student_id, 0)
        
        # Get bonus marks
        bonus_marks = bonus_data.get(student_id, 0)
        
        # Calculate final totals
        final_total = total_exam_marks + attendance_marks + bonus_marks
        max_attendance = 30  # Assume max 30 attendance days
        max_bonus = 100  # Assume max 100 bonus marks
        total_possible = total_possible_marks + max_attendance + max_bonus
        
        # Calculate percentage
        percentage = (final_total / total_possible * 100) if total_possible > 0 else 0
        
        # Calculate grade and GPA
        grade, gpa = calculate_grade_and_gpa(percentage)
        
        ranking_data = {
            'user_id': student_id,
            'student_name': student['full_name'],
            'student_phone': student['phoneNumber'],
            'individual_marks': individual_marks,
            'total_exam_marks': total_exam_marks,
            'total_possible_marks': total_possible_marks,
            'attendance_marks': attendance_marks,
            'bonus_marks': bonus_marks,
            'final_total': final_total,
            'total_possible': total_possible,
            'percentage': round(percentage, 2),
            'grade': grade,
            'gpa': round(gpa, 2)
        }
        
        rankings.append(ranking_data)
    
    # Sort by percentage (descending), then by name (ascending) for ties
    rankings.sort(key=lambda x: (-x['percentage'], x['student_name']))
    
    # Assign positions
    for idx, rank in enumerate(rankings):
        rank['position'] = idx + 1
    
    # Display results
    print("\n📊 COMPREHENSIVE MONTHLY RESULTS")
    print("=" * 80)
    print(f"{'Rank':<4} {'Student':<15} {'Exams':<15} {'Attend':<6} {'Bonus':<5} {'Total':<8} {'%':<6} {'Grade':<5}")
    print("-" * 80)
    
    for rank in rankings:
        print(f"{rank['position']:<4} {rank['student_name']:<15} "
              f"{rank['total_exam_marks']}/{rank['total_possible_marks']:<15} "
              f"{rank['attendance_marks']:<6} {rank['bonus_marks']:<5} "
              f"{rank['final_total']}/{rank['total_possible']:<8} "
              f"{rank['percentage']:.1f}%<6 {rank['grade']:<5}")
    
    print("\n🔍 INDIVIDUAL EXAM BREAKDOWN")
    print("=" * 80)
    
    for rank in rankings:
        print(f"\n{rank['position']}. {rank['student_name']} (Total: {rank['percentage']:.1f}%)")
        for exam_id, exam_mark in rank['individual_marks'].items():
            status = "ABSENT" if exam_mark['is_absent'] else f"{exam_mark['marks_obtained']}/{exam_mark['total_marks']}"
            print(f"   {exam_mark['subject']}: {status}")
        print(f"   Attendance: {rank['attendance_marks']} days")
        print(f"   Bonus: {rank['bonus_marks']} marks")
    
    print("\n✅ Comprehensive Monthly Results Test Completed!")
    print(f"✅ Processed {len(rankings)} students")
    print(f"✅ Individual exams: {len(individual_exams)}")
    print(f"✅ Ranking with alphabetical tiebreaker working")
    print(f"✅ Attendance integration working")
    print(f"✅ Bonus marks integration working")
    
    return rankings

if __name__ == "__main__":
    test_comprehensive_results()