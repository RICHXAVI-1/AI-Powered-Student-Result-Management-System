\# User Manual

\## AI-Powered Student Result Management System



\## Table of Contents

1\. \[Introduction](#introduction)

2\. \[Getting Started](#getting-started)

3\. \[Administrator Guide](#administrator-guide)

4\. \[Lecturer Guide](#lecturer-guide)

5\. \[Student Guide](#student-guide)

6\. \[AI Features Explained](#ai-features-explained)

7\. \[FAQs](#faqs)



---



\## Introduction



The AI-Powered Student Result Management System is a comprehensive web-based platform designed to automate and enhance the management of student academic results. The system combines traditional result processing with artificial intelligence to provide intelligent insights, performance predictions, and personalized recommendations.



\### Key Benefits

\- \*\*Automated Computation\*\*: Eliminates manual calculation errors

\- \*\*AI-Powered Insights\*\*: Predicts performance and identifies at-risk students

\- \*\*Real-time Access\*\*: Students and staff can access results anytime

\- \*\*Comprehensive Analytics\*\*: Data-driven decision support for administrators



---



\## Getting Started



\### Accessing the System



1\. Open your web browser

2\. Navigate to: `http://localhost:5000` (or your institution's URL)

3\. You will see the login page



\### First-Time Login



1\. Enter your username and password

2\. Click "Login"

3\. You will be redirected to your role-specific dashboard



\### User Roles



The system supports three user roles:



1\. \*\*Administrator\*\*

&nbsp;  - Full system access

&nbsp;  - Manage students, courses, and departments

&nbsp;  - View analytics and reports



2\. \*\*Lecturer\*\*

&nbsp;  - Enter and update student results

&nbsp;  - View course-specific data



3\. \*\*Student\*\*

&nbsp;  - View personal results

&nbsp;  - Access AI-powered performance insights



---



\## Administrator Guide



\### Dashboard Overview



After logging in as an administrator, you'll see:

\- \*\*Total Students\*\*: Current number of registered students

\- \*\*Total Courses\*\*: Number of courses in the system

\- \*\*Departments\*\*: Number of academic departments

\- \*\*Total Results\*\*: Number of result entries



\### Managing Students



\#### Adding a New Student



1\. Go to \*\*Admin Dashboard\*\* → \*\*Manage Students\*\*

2\. Click \*\*"Add New Student"\*\* button

3\. Fill in the form:

&nbsp;  - Matric Number (e.g., CSC/2024/001)

&nbsp;  - First Name

&nbsp;  - Last Name

&nbsp;  - Email Address

&nbsp;  - Department

&nbsp;  - Level (100, 200, 300, or 400)

4\. Click \*\*"Add Student"\*\*



The system automatically:

\- Creates a user account for the student

\- Sets default password as "password123"

\- Sends credentials (in future versions)



\#### Viewing Students



\- Navigate to \*\*Manage Students\*\*

\- View list of all registered students

\- Use search/filter options to find specific students



\#### Editing Student Information



1\. Find the student in the list

2\. Click the \*\*Edit\*\* (pencil) icon

3\. Update the required fields

4\. Click \*\*"Save Changes"\*\*



\### Managing Courses



\#### Adding a New Course



1\. Go to \*\*Admin Dashboard\*\* → \*\*Manage Courses\*\*

2\. Click \*\*"Add New Course"\*\*

3\. Fill in:

&nbsp;  - Course Code (e.g., CSC301)

&nbsp;  - Course Title

&nbsp;  - Credit Units (1-6)

&nbsp;  - Semester (First or Second)

&nbsp;  - Level (100-400)

&nbsp;  - Department

4\. Click \*\*"Add Course"\*\*



\### Viewing Analytics



\#### Accessing AI Analytics



1\. Go to \*\*Admin Dashboard\*\* → \*\*Analytics\*\*

2\. View the AI Analytics Dashboard showing:

&nbsp;  - Number of at-risk students

&nbsp;  - Performance distribution

&nbsp;  - Trend analysis



\#### Understanding At-Risk Students



The AI system identifies at-risk students based on:

\- Average score below 50

\- Two or more failed courses

\- Consistent declining performance trend

\- Recent scores below 45



\#### Taking Action



For at-risk students:

1\. Review their detailed performance

2\. Click \*\*"View"\*\* to see full academic history

3\. Click \*\*"Alert"\*\* to send intervention notice

4\. Coordinate with lecturers for academic support



\### Generating Reports



(Feature to be implemented in future versions)



---



\## Lecturer Guide



\### Dashboard Overview



The lecturer dashboard provides:

\- Quick access to result entry

\- List of available courses

\- System features overview



\### Entering Student Results



\#### Step-by-Step Process



1\. Go to \*\*Lecturer Dashboard\*\* → \*\*Enter Results\*\*

2\. Select the \*\*Student\*\* from the dropdown

3\. Select the \*\*Course\*\*

4\. Enter the \*\*Session\*\* (e.g., 2023/2024)

5\. Enter the \*\*Score\*\* (0-100)



\#### Understanding Automatic Grading



As you type the score, the system shows a preview:

\- \*\*Score 70-100\*\*: Grade A (5.0 points) - Excellent

\- \*\*Score 60-69\*\*: Grade B (4.0 points) - Very Good

\- \*\*Score 50-59\*\*: Grade C (3.0 points) - Good

\- \*\*Score 45-49\*\*: Grade D (2.0 points) - Fair

\- \*\*Score 40-44\*\*: Grade E (1.0 points) - Pass

\- \*\*Score 0-39\*\*: Grade F (0.0 points) - Fail



\#### Updating Results



To update an existing result:

1\. Enter the same student, course, and session

2\. Enter the new score

3\. The system will automatically update the record

4\. GPA/CGPA will be recalculated



\#### Important Notes



\- Results are immediately saved to the database

\- GPA is automatically calculated

\- CGPA is updated across all semesters

\- Students can view results in real-time



---



\## Student Guide



\### Viewing Your Dashboard



After logging in, your dashboard displays:



\#### Performance Summary Cards

1\. \*\*Matric Number\*\*: Your student ID

2\. \*\*Current CGPA\*\*: Your cumulative grade point average

3\. \*\*Level\*\*: Your current academic level

4\. \*\*AI Prediction\*\*: Performance category prediction



\#### AI Performance Analysis



\##### Performance Trends

\- \*\*Trend Status\*\*: Improving, Stable, or Declining

\- \*\*Improvement Score\*\*: Change in recent performance

\- \*\*Consistency\*\*: How stable your performance is (0-100%)

\- \*\*Average Score\*\*: Your overall average score



\##### AI Recommendations



The system provides personalized recommendations based on your performance:

\- Study strategies

\- Areas needing improvement

\- Academic support suggestions

\- Performance maintenance tips



\#### Performance Metrics



View detailed statistics:

\- \*\*Total Courses\*\*: Number of courses taken

\- \*\*Average Score\*\*: Your mean score across all courses

\- \*\*Passed Courses\*\*: Number of courses with passing grades

\- \*\*Failed Courses\*\*: Number of failed courses

\- \*\*Grade Distribution\*\*: Breakdown of your grades (A, B, C, D, E, F)



\#### Results Table



View your complete academic record:

\- Course Code and Title

\- Credit Units

\- Session

\- Score

\- Grade

\- Grade Point

\- Remarks



\### Understanding Your Performance Prediction



The AI system categorizes your performance as:



1\. \*\*Excellent\*\*

&nbsp;  - Average score ≥ 70

&nbsp;  - No failed courses

&nbsp;  - Consistent high performance



2\. \*\*Good\*\*

&nbsp;  - Average score ≥ 60

&nbsp;  - Positive performance trend

&nbsp;  - Few or no failures



3\. \*\*Average\*\*

&nbsp;  - Average score ≥ 50

&nbsp;  - Stable performance

&nbsp;  - Maximum 1 failed course



4\. \*\*At-Risk\*\*

&nbsp;  - Average score < 50

&nbsp;  - Multiple failures

&nbsp;  - Declining performance trend



\### Taking Action on Recommendations



1\. \*\*Review AI Recommendations\*\*: Read carefully the personalized advice

2\. \*\*Identify Weak Areas\*\*: Look at courses with low grades

3\. \*\*Seek Help\*\*: Contact lecturers during office hours

4\. \*\*Join Study Groups\*\*: Collaborate with peers

5\. \*\*Use Resources\*\*: Utilize library and online materials



---



\## AI Features Explained



\### How the AI System Works



\#### Performance Prediction



The AI uses machine learning algorithms to analyze:

\- Historical academic performance

\- Score trends over time

\- Grade patterns

\- Attendance data (when available)

\- Course difficulty levels



\#### Trend Analysis



The system calculates:

\- \*\*Recent vs. Earlier Performance\*\*: Compares latest scores with previous ones

\- \*\*Consistency Score\*\*: Measures stability using statistical variance

\- \*\*Trajectory\*\*: Determines if performance is improving, stable, or declining



\#### At-Risk Identification



Multiple criteria are evaluated:

```

IF average\_score < 50 OR

&nbsp;  failed\_courses >= 2 OR

&nbsp;  recent\_score < 45 OR

&nbsp;  (score\[n] < score\[n-1] < score\[n-2])

THEN flag as at-risk

```



\#### Recommendation Engine



The AI generates recommendations based on:

\- Performance level

\- Trend direction

\- Number of failures

\- GPA status

\- Comparison with peers



\### Data Privacy and Security



\- All data is encrypted in the database

\- Role-based access control

\- Only authorized users can view sensitive information

\- Audit trails for data modifications

\- Secure password hashing



---



\## FAQs



\### General Questions



\*\*Q: How often is the data updated?\*\*

A: Results and analytics are updated in real-time as lecturers enter data.



\*\*Q: Can I access the system on mobile devices?\*\*

A: Yes, the system is responsive and works on smartphones and tablets.



\*\*Q: What browsers are supported?\*\*

A: Chrome, Firefox, Safari, and Edge (latest versions).



\### For Students



\*\*Q: When will my results be available?\*\*

A: Results appear immediately after your lecturer enters them.



\*\*Q: Why does my CGPA differ from my manual calculation?\*\*

A: The system uses weighted averages based on credit units. Verify your calculation includes credit weighting.



\*\*Q: Can I dispute a result?\*\*

A: Contact your lecturer or department administrator for result inquiries.



\*\*Q: What does "At-Risk" prediction mean?\*\*

A: It's an early warning that you may need academic support. Contact your academic advisor.



\### For Lecturers



\*\*Q: Can I edit a result after submitting?\*\*

A: Yes, enter the same student/course/session with the new score.



\*\*Q: What if I enter the wrong score?\*\*

A: Simply re-enter the correct score; the system will update automatically.



\*\*Q: How is GPA calculated?\*\*

A: GPA = (Sum of (Grade Point × Credit Unit)) / (Total Credit Units)



\### For Administrators



\*\*Q: How do I reset a student's password?\*\*

A: Currently requires database access. Feature will be added in future versions.



\*\*Q: Can I export data to Excel?\*\*

A: Export functionality will be added in future updates.



\*\*Q: How do I backup the database?\*\*

A: Use MySQL backup commands (see Installation Guide).



\### Technical Questions



\*\*Q: Is my data secure?\*\*

A: Yes, the system uses industry-standard security practices including password hashing and encrypted connections.



\*\*Q: What happens if the system crashes?\*\*

A: All data is stored in the MySQL database and persists. Simply restart the application.



\*\*Q: Can multiple users access simultaneously?\*\*

A: Yes, the system supports concurrent users.



---



\## Getting Help



\### Contact Support



For technical assistance:

1\. Check this manual first

2\. Review the README.md file

3\. Contact your system administrator

4\. Check error messages for specific issues



\### Reporting Issues



When reporting problems, include:

\- Your user role

\- What you were trying to do

\- Error message (if any)

\- Screenshot (if applicable)

\- Browser and operating system



\### Feature Requests



To suggest new features:

1\. Document the proposed feature

2\. Explain the benefit

3\. Submit to system administrator



---



\## Best Practices



\### For All Users



1\. \*\*Security\*\*

&nbsp;  - Change default password on first login

&nbsp;  - Don't share your credentials

&nbsp;  - Log out after use

&nbsp;  - Use strong passwords



2\. \*\*Data Entry\*\*

&nbsp;  - Double-check information before submitting

&nbsp;  - Use correct session format (e.g., 2023/2024)

&nbsp;  - Verify student identification



\### For Lecturers



1\. \*\*Result Entry\*\*

&nbsp;  - Enter results promptly

&nbsp;  - Verify scores before submission

&nbsp;  - Update incorrect entries immediately

&nbsp;  - Maintain backup records



\### For Students



1\. \*\*Monitoring Performance\*\*

&nbsp;  - Check results regularly

&nbsp;  - Act on AI recommendations

&nbsp;  - Track your progress over time

&nbsp;  - Seek help early if struggling



---



\## Conclusion



The AI-Powered Student Result Management System streamlines academic result management while providing intelligent insights to improve student outcomes. By leveraging artificial intelligence, the system helps identify struggling students early and provides data-driven recommendations for academic success.



For additional information or support, please contact your institution's IT department or system administrator.



---



\*\*Version\*\*: 1.0.0  

\*\*Last Updated\*\*: January 2024  

\*\*Developed by\*\*: TEMITOPE, Adeleke University

