# SmartGardenHub - Student Management System

A comprehensive Flask-based student management system for educational institutions.

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/8ytgggygt/saro.git
cd saro
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run the application (creates database automatically)
python run.py

# Access at http://127.0.0.1:3001
```

Default login: Phone `01712345678`, Password `admin123` (after running `create_default_users.py`)

## 🌟 Features

- **Multi-Role Authentication**: Support for Students, Teachers, and Super Users
- **Student Management**: CRUD operations for student records
- **Batch Management**: Organize students into batches/classes
- **Attendance Tracking**: Mark and monitor student attendance
- **Online Exams**: Create and manage online assessments
- **Monthly Exams**: Track regular monthly examinations
- **SMS Integration**: Send notifications to parents/students
- **Dashboard Analytics**: Real-time statistics and insights

## 🚀 Tech Stack

- **Backend**: Flask 3.1.2 (Python)
- **Database**: SQLite (dev) / MySQL (production)
- **ORM**: SQLAlchemy 2.0.44
- **Authentication**: Flask-Session with Bcrypt password hashing
- **Frontend**: HTML, CSS, JavaScript
- **SMS**: BulkSMSBD API (hardcoded, ready to use)
- **AI**: Google Gemini API integration (optional)

## 📋 Prerequisites

- Python 3.8+ (3.12 recommended)
- pip (Python package manager)
- Git

**Optional** (for production):
- MySQL Server 8.0+

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/8ytgggygt/saro.git
   cd saro
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables (Optional)**
   
   Copy the example file and customize:
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```
   
   **Note**: The app works out-of-the-box with SQLite (no MySQL setup needed for development)

5. **Initialize database (Optional)**
   
   The database is created automatically on first run. To create default test users:
   ```bash
   python create_default_users.py
   ```

6. **Run the application**
   ```bash
   python run.py
   ```

   Server will start at `http://127.0.0.1:3001` (or `http://0.0.0.0:3001`)

   Alternative method:
   ```bash
   python app.py
   ```

## 👥 Default Login Credentials

After running `create_default_users.py`:

**Admin Account:**
- Phone: `01712345678`
- Password: `admin123`

**Teacher Account:**
- Phone: `01812345678`
- Password: `teacher123`

**Student Account:**
- Phone: `01912345678`
- Password: `student123`

## 📁 Project Structure

```
saro/
├── app.py                 # Main application entry point
├── run.py                 # Application runner with proper config
├── config.py              # Configuration settings (SQLite/MySQL)
├── models.py              # Database models (SQLAlchemy)
├── routes/                # API routes (Blueprints)
│   ├── auth.py            # Authentication routes
│   ├── students.py        # Student management
│   ├── batches.py         # Batch/class management
│   ├── attendance.py      # Attendance tracking
│   ├── exams.py           # Online exams
│   ├── monthly_exams.py   # Monthly examinations
│   ├── results.py         # Results management
│   ├── fees.py            # Fee management
│   ├── sms.py             # SMS integration
│   ├── ai.py              # AI features
│   ├── dashboard.py       # Dashboard analytics
│   ├── settings.py        # Settings management
│   └── templates.py       # Template routes
├── templates/             # HTML templates
│   └── templates/         # Nested templates directory
├── static/                # Static files (CSS, JS, images)
│   └── static/            # Nested static directory
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
├── DATABASE_SETUP.md      # Comprehensive database documentation
└── README.md              # This file
```

## 📊 Database Configuration

### Development (Default - SQLite)
- **Database File**: `smartgardenhub.db` (created automatically)
- **Location**: Project root directory
- **Advantages**: Zero configuration, perfect for testing
- **Setup**: None required - database created on first run

### Production (MySQL)
- **Configuration**: Via `.env` file
- **Setup Instructions**: See `DATABASE_SETUP.md`
- **Migration Tools**: Provided migration scripts

For detailed database documentation, schema, and operations, see [`DATABASE_SETUP.md`](DATABASE_SETUP.md).

## 🔐 Security Features

- Secure password hashing using Werkzeug
- Role-based access control (RBAC)
- Session management
- Local password storage for students
- SQL injection protection via SQLAlchemy ORM

## 📝 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user

### Students
- `GET /api/students` - List all students
- `POST /api/students` - Create new student
- `GET /api/students/{id}` - Get student details
- `PUT /api/students/{id}` - Update student
- `DELETE /api/students/{id}` - Delete student
- `GET /api/students/passwords` - Get student passwords (Teacher only)

### Batches
- `GET /api/batches` - List all batches
- `POST /api/batches` - Create new batch
- `GET /api/batches/{id}` - Get batch details
- `PUT /api/batches/{id}` - Update batch
- `DELETE /api/batches/{id}` - Delete batch

### Attendance
- `POST /api/attendance` - Mark attendance
- `GET /api/attendance` - Get attendance records

### Exams
- `GET /api/exams` - List all exams
- `POST /api/exams` - Create new exam
- `GET /api/exams/{id}/results` - Get exam results

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

**Golam Sarowar Sir**

## 🚢 Deployment

### Production Deployment

1. **Setup MySQL database** (see `DATABASE_SETUP.md`)
2. **Configure production environment**:
   ```bash
   cp .env.example .env
   # Edit .env with production values
   export FLASK_ENV=production
   ```
3. **Use Gunicorn** for production server:
   ```bash
   pip install gunicorn
   gunicorn -c gunicorn.conf.py "app:create_app()"
   ```

### Docker Deployment (Coming Soon)

Docker support with containerized MySQL will be added in future releases.

## � Documentation

- **[DATABASE_SETUP.md](DATABASE_SETUP.md)** - Complete database documentation
- **[.env.example](.env.example)** - Environment configuration template
- **API Endpoints** - See "API Endpoints" section above

## 🆘 Support

For support:
- Open an issue in the [GitHub repository](https://github.com/8ytgggygt/saro/issues)
- Review documentation files
- Check logs in `server.log`

## 📱 Contact

- **GitHub**: [@8ytgggygt](https://github.com/8ytgggygt)
- **Repository**: [saro](https://github.com/8ytgggygt/saro)

---

**Built with ❤️ for educational institutions**

### Project Status
- ✅ Core Features: Complete
- ✅ Database: SQLite (dev) + MySQL (prod)
- ✅ Authentication: Complete
- ✅ Student Management: Complete
- ✅ Attendance System: Complete
- ✅ Exam System: Complete
- ✅ Results Management: Complete
- 🚧 Docker Support: Coming Soon

**Version**: 1.0.0  
**Last Updated**: October 19, 2025
