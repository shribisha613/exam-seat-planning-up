# 🎯 Exam Seat Planning System

A comprehensive Django-based examination seating arrangement system designed for universities and educational institutions to automate and streamline the exam hall allocation process.

## ✨ Features

- **🏛️ Multi-Hall Management**: Support for multiple examination halls with configurable seating layouts
- **📊 Automated Seat Assignment**: Intelligent algorithm for fair and random seat distribution
- **👥 Student Management**: Comprehensive student database with course and batch management
- **📅 Exam Scheduling**: Create and manage multiple exam sessions with date/time slots
- **🔄 Conflict Prevention**: Automatic detection and prevention of scheduling conflicts
- **📋 Seating Charts**: Generate printable seating arrangements and hall-wise reports
- **🔐 Role-based Access**: Admin, faculty, and student portals with appropriate permissions
- **📱 Responsive Design**: Mobile-friendly interface for easy access on all devices
- **📈 Analytics Dashboard**: Insights into hall utilization and exam statistics
- **🔍 Search & Filter**: Quick search functionality for students, exams, and halls

## 🛠️ Technology Stack

- **Backend**: Django 4.x (Python Web Framework)
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap
- **Authentication**: Django's built-in authentication system
- **Reporting**: PDF generation for seating charts
- **Deployment**: Compatible with Heroku, AWS, and other cloud platforms

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for version control)
- Virtual environment (recommended)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/shribisha613/exam-seat-planning-up.git
cd exam-seat-planning-up
```

### 2. Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
```bash
# Apply database migrations
python manage.py migrate

# Create superuser account
python manage.py createsuperuser

# Load sample data (optional)
python manage.py loaddata fixtures/sample_data.json
```

### 5. Run the Development Server
```bash
python manage.py runserver
```

### 6. Access the Application
- **Main Application**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **API Documentation**: http://127.0.0.1:8000/api/docs/ (if available)

## 📖 Usage Guide

### For Administrators

1. **Login** to the admin panel using your superuser credentials
2. **Add Halls**: Configure examination halls with seating capacity and layout
3. **Register Students**: Import or manually add student information
4. **Create Exams**: Schedule exams with dates, times, and subject details
5. **Generate Seating**: Use the automated seat assignment feature
6. **Print Reports**: Generate and download seating charts for each hall

### For Faculty

1. **Login** with faculty credentials
2. **View Assignments**: Check exam invigilation duties
3. **Access Seating Charts**: Download hall-wise seating arrangements
4. **Monitor Students**: View student lists for assigned halls

### For Students

1. **Login** with student credentials
2. **View Exam Schedule**: Check upcoming exam dates and times
3. **Find Seat**: Look up assigned seat number and hall
4. **Download Admit Card**: Generate exam admit card with seating details

## 🏗️ Project Structure

```
exam-seat-planning-up/
├── apps/
│   ├── core/                 # Core application logic
│   ├── halls/                # Hall management
│   ├── students/             # Student management
│   ├── exams/                # Exam scheduling
│   └── reports/              # Report generation
├── static/                   # Static files (CSS, JS, images)
├── templates/                # HTML templates
├── media/                    # User uploaded files
├── config/                   # Django settings
├── requirements.txt          # Python dependencies
├── manage.py                 # Django management script
└── README.md                # Project documentation
```

## ⚙️ Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password
```

### Database Configuration
For production, update `settings.py` to use PostgreSQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'exam_seating_db',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 🧪 Testing

Run the test suite:
```bash
# Run all tests
python manage.py test

# Run tests with coverage
coverage run manage.py test
coverage report
coverage html
```

## 🚢 Deployment

### Using Heroku
1. Install Heroku CLI
2. Login to Heroku: `heroku login`
3. Create app: `heroku create your-app-name`
4. Set environment variables: `heroku config:set SECRET_KEY=your-key`
5. Deploy: `git push heroku main`

### Using Docker
```bash
# Build image
docker build -t exam-seat-planning .

# Run container
docker run -p 8000:8000 exam-seat-planning
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Write comprehensive tests for new features
- Update documentation for any API changes
- Use meaningful commit messages
- Ensure all tests pass before submitting PR

## 🐛 Troubleshooting

### Common Issues

**Module Not Found Error**
```bash
pip install -r requirements.txt
```

**Database Migration Issues**
```bash
python manage.py makemigrations
python manage.py migrate --run-syncdb
```

**Static Files Not Loading**
```bash
python manage.py collectstatic
```

**Permission Denied Errors**
- Check file permissions
- Ensure virtual environment is activated
- Run with appropriate user privileges

## 📊 API Documentation

The system provides RESTful APIs for integration:

- `GET /api/students/` - List all students
- `POST /api/exams/` - Create new exam
- `GET /api/halls/` - List examination halls
- `POST /api/seating/generate/` - Generate seating arrangement

For detailed API documentation, visit `/api/docs/` after starting the server.

## 🔐 Security

- All user inputs are validated and sanitized
- CSRF protection enabled for all forms
- Secure session management
- SQL injection prevention through Django ORM
- Regular security updates and patches

## 📈 Performance

- Database query optimization
- Caching for frequently accessed data
- Pagination for large datasets
- Compressed static files
- Efficient seating algorithm with O(n log n) complexity

## 🌟 Roadmap

- [ ] Mobile app for iOS and Android
- [ ] Integration with university management systems
- [ ] Advanced analytics and reporting
- [ ] Multi-language support
- [ ] Real-time notifications
- [ ] Barcode/QR code support for admit cards
- [ ] AI-powered seat optimization

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **shribisha613** - *Initial work* - [GitHub](https://github.com/shribisha613)

## 🙏 Acknowledgments

- Django community for the excellent framework
- Bootstrap team for responsive design components
- Contributors and testers who helped improve the system
- Educational institutions that provided requirements and feedback

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/shribisha613/exam-seat-planning-up/issues)
- **Discussions**: [GitHub Discussions](https://github.com/shribisha613/exam-seat-planning-up/discussions)
- **Email**: Create an issue for support

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [Git Workflow Guide](https://guides.github.com/introduction/flow/)

---

**Made with ❤️ for educational institutions worldwide**
