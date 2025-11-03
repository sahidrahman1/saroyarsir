# Database Setup Guide

## Overview

SmartGardenHub uses SQLAlchemy ORM with support for both SQLite (development) and MySQL (production).

## Database Architecture

### Development Environment
- **Database**: SQLite
- **Location**: `smartgardenhub.db` in project root
- **Advantages**: Zero configuration, portable, perfect for development

### Production Environment
- **Database**: MySQL 8.0+
- **Configuration**: Via environment variables in `.env`
- **Migration**: Use provided migration scripts

## Quick Start (Development)

The application automatically creates the SQLite database and tables on first run:

```bash
# 1. Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 2. Run the application (creates database automatically)
python run.py

# 3. (Optional) Create default test users
python create_default_users.py
```

## Database Schema

### Core Tables

#### 1. **users**
Main user table for all system users (students, teachers, super users)

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Unique user identifier |
| phone | String(20) | Phone number (unique login ID) |
| password | String(255) | Hashed password |
| name | String(100) | User's full name |
| role | Enum | 'student', 'teacher', 'super_user' |
| created_at | DateTime | Account creation timestamp |
| updated_at | DateTime | Last update timestamp |

#### 2. **batches**
Academic batches/classes

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Unique batch identifier |
| name | String(100) | Batch name (e.g., "HSC 2025") |
| description | Text | Batch description |
| teacher_id | Integer (FK) | Teacher assigned to batch |
| created_at | DateTime | Creation timestamp |

#### 3. **batch_students**
Many-to-many relationship between batches and students

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Unique enrollment ID |
| batch_id | Integer (FK) | Reference to batch |
| student_id | Integer (FK) | Reference to student |
| roll_number | Integer | Student's roll number in batch |
| enrolled_at | DateTime | Enrollment timestamp |

#### 4. **attendance**
Daily attendance records

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Unique attendance record ID |
| batch_id | Integer (FK) | Reference to batch |
| student_id | Integer (FK) | Reference to student |
| date | Date | Attendance date |
| status | Enum | 'present', 'absent', 'late' |
| marked_by | Integer (FK) | Teacher who marked attendance |
| marked_at | DateTime | Marking timestamp |

#### 5. **exams**
Online exams/assessments

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Unique exam identifier |
| title | String(200) | Exam title |
| batch_id | Integer (FK) | Target batch |
| duration | Integer | Duration in minutes |
| total_marks | Integer | Total marks |
| start_time | DateTime | Exam start time |
| end_time | DateTime | Exam end time |
| created_by | Integer (FK) | Teacher who created exam |

#### 6. **questions**
Exam questions

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Unique question ID |
| exam_id | Integer (FK) | Reference to exam |
| question_text | Text | Question content |
| option_a | String(500) | Option A |
| option_b | String(500) | Option B |
| option_c | String(500) | Option C |
| option_d | String(500) | Option D |
| correct_answer | Enum | 'A', 'B', 'C', 'D' |
| marks | Integer | Marks for this question |

#### 7. **exam_results**
Student exam performance

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Unique result ID |
| exam_id | Integer (FK) | Reference to exam |
| student_id | Integer (FK) | Reference to student |
| score | Integer | Student's score |
| total_marks | Integer | Total possible marks |
| percentage | Float | Score percentage |
| rank | Integer | Rank in batch |
| submitted_at | DateTime | Submission timestamp |

#### 8. **monthly_exams**
Monthly examination records

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Unique exam ID |
| title | String(200) | Exam title |
| exam_date | Date | Date of examination |
| batch_id | Integer (FK) | Reference to batch |
| subject | String(100) | Subject name |
| total_marks | Integer | Total marks |
| created_by | Integer (FK) | Teacher who created |

#### 9. **monthly_exam_results**
Monthly exam student results

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Unique result ID |
| exam_id | Integer (FK) | Reference to monthly exam |
| student_id | Integer (FK) | Reference to student |
| marks_obtained | Integer | Marks scored |
| total_marks | Integer | Total possible marks |
| percentage | Float | Score percentage |
| rank | Integer | Rank in batch |

#### 10. **fees**
Fee management

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Unique fee record ID |
| student_id | Integer (FK) | Reference to student |
| amount | Decimal | Fee amount |
| due_date | Date | Payment due date |
| paid_date | Date | Actual payment date |
| status | Enum | 'pending', 'paid', 'overdue' |

#### 11. **sms_templates**
SMS message templates

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Template ID |
| name | String(100) | Template name |
| template | Text | Message template |
| category | String(50) | Template category |

#### 12. **sms_balance**
SMS credit balance tracking

| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Balance record ID |
| balance | Integer | Current SMS balance |
| last_updated | DateTime | Last update timestamp |

## Database Initialization

### Automatic Initialization (Recommended)

The application automatically creates all tables on first run:

```python
# This happens automatically in app.py
with app.app_context():
    db.create_all()
```

### Manual Initialization

If you need to manually initialize the database:

```bash
# Using init_db.py script
python init_db.py

# Or using Python shell
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('Database initialized!')"
```

### Creating Default Users

After database creation, create default test users:

```bash
python create_default_users.py
```

This creates:
- **Super User**: Phone: `01712345678`, Password: `admin123`
- **Teacher**: Phone: `01812345678`, Password: `teacher123`
- **Student**: Phone: `01912345678`, Password: `student123`

## Database Migrations

### SQLite to MySQL Migration (Production)

When moving from development (SQLite) to production (MySQL):

1. **Setup MySQL database**:
```sql
CREATE DATABASE smartgardenhub CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'smartgarden'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON smartgardenhub.* TO 'smartgarden'@'localhost';
FLUSH PRIVILEGES;
```

2. **Update .env file**:
```bash
FLASK_ENV=production
MYSQL_HOST=localhost
MYSQL_USER=smartgarden
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=smartgardenhub
```

3. **Run migration script**:
```bash
python migrate_database.py
```

### Adding New Columns/Tables

When schema changes are needed:

1. **Update models.py** with new fields/tables
2. **Drop and recreate** (development only):
```bash
rm smartgardenhub.db
python run.py  # Recreates with new schema
```

3. **For production**, use migration tools like Alembic:
```bash
pip install alembic
alembic init migrations
alembic revision --autogenerate -m "Add new field"
alembic upgrade head
```

## Database Backup & Restore

### SQLite Backup

```bash
# Backup
cp smartgardenhub.db backups/smartgardenhub_$(date +%Y%m%d).db

# Restore
cp backups/smartgardenhub_20251019.db smartgardenhub.db
```

### MySQL Backup

```bash
# Backup
mysqldump -u root -p smartgardenhub > backups/smartgardenhub_$(date +%Y%m%d).sql

# Restore
mysql -u root -p smartgardenhub < backups/smartgardenhub_20251019.sql
```

## Common Database Operations

### Query Examples

```python
from app import create_app, db
from models import User, Batch, Student

app = create_app()
with app.app_context():
    # Get all students
    students = User.query.filter_by(role='student').all()
    
    # Get batch with students
    batch = Batch.query.get(1)
    students_in_batch = batch.students
    
    # Create new user
    new_student = User(
        phone='01900000000',
        name='Test Student',
        role='student'
    )
    new_student.set_password('password123')
    db.session.add(new_student)
    db.session.commit()
```

### Database Inspection

```bash
# SQLite
sqlite3 smartgardenhub.db ".tables"
sqlite3 smartgardenhub.db ".schema users"
sqlite3 smartgardenhub.db "SELECT * FROM users LIMIT 5;"

# MySQL
mysql -u root -p smartgardenhub -e "SHOW TABLES;"
mysql -u root -p smartgardenhub -e "DESCRIBE users;"
mysql -u root -p smartgardenhub -e "SELECT * FROM users LIMIT 5;"
```

## Troubleshooting

### Database Locked (SQLite)

If you see "database is locked" error:
```bash
# Kill any hanging processes
pkill -f "python.*run.py"
# Remove lock
rm smartgardenhub.db-journal
```

### Connection Errors (MySQL)

```bash
# Test MySQL connection
mysql -u root -p -e "SELECT 1;"

# Check if MySQL is running
sudo systemctl status mysql

# Reset MySQL password if needed
sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_password';"
```

### Missing Tables

```bash
# Recreate all tables
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.drop_all(); db.create_all(); print('Tables recreated!')"
```

## Database Security

1. **Never commit** `.env` or `smartgardenhub.db` to Git
2. **Use strong passwords** for MySQL in production
3. **Restrict database user permissions** appropriately
4. **Regular backups** of production data
5. **Use SSL/TLS** for MySQL connections in production

## Performance Optimization

### SQLite

```python
# Add indexes in models.py
class User(db.Model):
    __tablename__ = 'users'
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
```

### MySQL

```sql
-- Add indexes for frequently queried columns
CREATE INDEX idx_user_role ON users(role);
CREATE INDEX idx_attendance_date ON attendance(date);
CREATE INDEX idx_exam_batch ON exams(batch_id);
```

## Support

For database-related issues:
1. Check this documentation
2. Review `models.py` for schema definitions
3. Check application logs in `server.log`
4. Inspect database directly using sqlite3/mysql commands

---

**Last Updated**: October 19, 2025
**Database Version**: 1.0
**Compatible With**: SmartGardenHub v1.0+
