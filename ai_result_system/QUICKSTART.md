# Quick Start Guide
## AI-Powered Student Result Management System

Get started in 5 minutes!

## Prerequisites
- Python 3.8+
- MySQL 8.0+
- Web browser

## Installation (3 Steps)

### 1. Install Dependencies
```bash
cd ai_result_system
pip install -r requirements.txt
```

### 2. Setup Database
```bash
# Login to MySQL
mysql -u root -p

# Create database
CREATE DATABASE result_management;
EXIT;
```

Update `app.py` line 15 with your MySQL credentials:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:YOUR_PASSWORD@localhost/result_management'
```

### 3. Initialize & Run
```bash
# Initialize database with sample data
python init_db.py

# Start the application
python app.py
```

## Access the System

Open browser: **http://localhost:5000**

### Login Credentials

**Admin**
- Username: `admin`
- Password: `admin123`

**Lecturer**
- Username: `lecturer1`
- Password: `lecturer123`

**Student**
- Username: `CSC/2021/001`
- Password: `password123`

## Quick Tour

### As Admin
1. Login with admin credentials
2. Click "Manage Students" to see registered students
3. Click "Analytics" to see AI-powered insights
4. View at-risk students and performance trends

### As Lecturer
1. Login with lecturer credentials
2. Click "Enter Results"
3. Select student, course, and enter score
4. Watch automatic grade calculation!

### As Student
1. Login with student credentials
2. View your CGPA and results
3. Check AI performance prediction
4. Read personalized recommendations

## Key Features at a Glance

✅ **Automated Grading** - Scores instantly converted to grades  
✅ **GPA/CGPA Calculation** - Automatic computation  
✅ **AI Predictions** - Performance trend analysis  
✅ **At-Risk Detection** - Early warning system  
✅ **Recommendations** - Personalized academic advice  

## Grading Scale

| Score | Grade | Points |
|-------|-------|--------|
| 70-100 | A | 5.0 |
| 60-69 | B | 4.0 |
| 50-59 | C | 3.0 |
| 45-49 | D | 2.0 |
| 40-44 | E | 1.0 |
| 0-39 | F | 0.0 |

## Need Help?

📚 **Full Documentation**
- `README.md` - Complete overview
- `INSTALLATION.md` - Detailed setup
- `USER_MANUAL.md` - User guide

🐛 **Troubleshooting**
- Database error? Check MySQL is running
- Import error? Run `pip install -r requirements.txt`
- Port busy? Change port in `app.py`

## Next Steps

1. ✅ Change default passwords
2. ✅ Add your institution's students
3. ✅ Configure courses
4. ✅ Customize grading scale (if needed)
5. ✅ Start entering results!

---

**Enjoy using the AI-Powered Result Management System!** 🎓