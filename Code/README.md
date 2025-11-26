# SAP Project System Reports - Django Web Application

A comprehensive web-based reporting system for SAP Project System data analysis. This application processes SAP exports (DAT, HTML, Excel files) and generates professionally formatted Excel reports with advanced analytics, WBS classification, and interactive dashboards.

## Features

- **7 Report Types**:
  - Budget Report (S_ALR_87013558)
  - Budget Updates (S_ALR_87013560)
  - Budget Variance (S_ALR_87013557)
  - Plan Variance (S_ALR_87013532)
  - Project Type Wise (CN41N)
  - Glimps of Projects (Analytics Dashboard)
  - Project Analysis (Multi-file Processing)

- **Advanced Capabilities**:
  - WBS (Work Breakdown Structure) automatic classification
  - Indian currency formatting (₹ with lakh/crore separators)
  - Professional Excel styling with conditional formatting
  - Interactive web preview of data before download
  - Master data integration from WBS_NAMES.XLSX
  - Error handling and logging

- **Security**:
  - CSRF protection
  - File upload validation
  - Environment-based configuration
  - Secure file handling

## System Requirements

- Python 3.8 or higher
- 100MB+ disk space for uploads and reports
- Modern web browser (Chrome, Firefox, Edge, Safari)

## Installation

### 1. Clone or Download the Project

```bash
cd /path/to/PS-Reports/Code
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv

# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` and update the following:

```env
# Generate a new SECRET_KEY for production
SECRET_KEY=your-secret-key-here

# Set to False in production
DEBUG=True

# Add your server IP/domain
ALLOWED_HOSTS=localhost,127.0.0.1,your-server-ip
```

**Generate a new SECRET_KEY** (important for production):

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Database Setup

```bash
# Create database tables
python manage.py migrate

# Create an admin user
python manage.py createsuperuser
```

Follow the prompts to create your admin account.

### 6. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 7. Prepare Master Data

Place your **WBS_NAMES.XLSX** file in the `data/` directory. This file contains the WBS element descriptions used for mapping.

To import master data into the database:

```bash
python manage.py import_master_data
```

## Running the Application

### Development Server

```bash
python manage.py runserver
```

Access the application at: **http://localhost:8000**

To allow access from other machines on your network:

```bash
python manage.py runserver 0.0.0.0:8000
```

### Production Deployment

For production deployment, use a proper WSGI server like Gunicorn:

```bash
# Install gunicorn (already in requirements.txt)
pip install gunicorn

# Run with gunicorn
gunicorn django_project.wsgi:application --bind 0.0.0.0:8000
```

For better performance and security, use Nginx as a reverse proxy in front of Gunicorn.

## Usage

### Accessing the Dashboard

1. Open your browser and go to `http://localhost:8000`
2. You'll see the main dashboard with all available reports

### Generating Reports

1. Click on any report type (e.g., "Budget Report")
2. Upload your SAP export file (DAT, HTML, or Excel depending on report type)
3. Click "Generate Report"
4. Preview the data in your browser
5. Download the formatted Excel report

### Admin Interface

Access the admin panel at `http://localhost:8000/admin` to:
- Manage WBS Elements, Company Codes, and Project Types
- View uploaded files and generated reports
- Monitor system activity

## File Structure

```
Code/
├── manage.py                   # Django management script
├── requirements.txt            # Python dependencies
├── .env                        # Environment configuration (not in git)
├── .env.example               # Environment template
├── db.sqlite3                 # SQLite database
├── django_project/            # Django project settings
│   ├── settings.py            # Main configuration
│   ├── urls.py                # URL routing
│   └── wsgi.py                # WSGI configuration
├── reports/                   # Main application
│   ├── models.py              # Database models
│   ├── views.py               # View controllers
│   ├── urls.py                # App URL routing
│   ├── forms.py               # Upload forms
│   ├── admin.py               # Admin interface
│   ├── services/              # Business logic
│   │   ├── formatting.py      # Excel formatting
│   │   ├── data_processing.py # Data processing
│   │   ├── error_handling.py  # Error management
│   │   ├── budget_report_service.py
│   │   ├── budget_updates_service.py
│   │   ├── budget_variance_service.py
│   │   ├── plan_variance_service.py
│   │   ├── project_type_wise_service.py
│   │   └── glimps_of_projects_service.py
│   ├── templates/             # HTML templates
│   │   ├── base.html          # Base template
│   │   └── reports/           # Report templates
│   ├── static/                # Static files (CSS, JS)
│   └── management/            # Django commands
├── data/                      # Data directory
│   ├── uploads/               # Uploaded files
│   ├── reports/               # Generated reports
│   └── WBS_NAMES.XLSX        # Master data file
├── staticfiles/              # Collected static files
└── config.py                 # Application configuration
```

## Configuration

### Business Logic Configuration

Edit `config.py` to customize:

- **Company Codes**: Mapping of short codes to full names (NL → NLCIL)
- **Project Types**: S, I, N, C, E, F, R, O, M classifications
- **Excel Formatting**: Fonts, colors, currency format
- **Regex Patterns**: WBS element patterns and validation

### Django Settings

Edit `django_project/settings.py` for:

- Database configuration
- Static files settings
- Middleware configuration
- Installed apps

## Troubleshooting

### Import Error: No module named 'decouple'

```bash
pip install python-decouple
```

### Database Migration Errors

```bash
# Reset migrations (CAUTION: Deletes data)
python manage.py migrate --run-syncdb
```

### Static Files Not Loading

```bash
python manage.py collectstatic --clear --noinput
```

### WBS Master Data Not Found

Ensure `WBS_NAMES.XLSX` is in the `data/` directory and run:

```bash
python manage.py import_master_data
```

### Permission Errors on Linux

```bash
chmod +x manage.py
chmod -R 755 data/
```

## Development

### Running Tests

```bash
# Run all tests
python manage.py test

# Run tests with coverage
coverage run --source='.' manage.py test
coverage report
```

### Code Quality

```bash
# Format code with black
black .

# Check code style
flake8 .
```

### Creating a New Report Type

1. Create a new service file in `reports/services/`
2. Implement the report generation function
3. Add a view in `reports/views.py`
4. Add a URL pattern in `reports/urls.py`
5. Create a template in `reports/templates/reports/`
6. Add the report to the dashboard

## Security Considerations

### For Production Deployment

1. **Change SECRET_KEY**: Generate a new secret key
2. **Set DEBUG=False**: Disable debug mode
3. **Use HTTPS**: Configure SSL/TLS certificates
4. **File Upload Limits**: Configure MAX_UPLOAD_SIZE in .env
5. **Database**: Consider PostgreSQL instead of SQLite
6. **Backups**: Implement regular database backups
7. **Logging**: Configure centralized logging
8. **Firewall**: Restrict access to necessary ports

### Environment Variables

Never commit `.env` file to version control. It contains sensitive information.

## Support & Documentation

### Additional Documentation

- See `Markdown/DJANGO_MIGRATION_PLAN.md` for migration details
- See `Markdown/IMPLEMENTATION_CHECKLIST.md` for implementation progress
- See `Markdown/CLAUDE.md` for AI assistant guidance

### Common Issues

1. **File upload fails**: Check file permissions on `data/uploads/`
2. **Excel download fails**: Check `data/reports/` directory permissions
3. **WBS mapping not working**: Verify WBS_NAMES.XLSX is loaded

## License

Internal use only - SAP Project System Reports

## Version History

- **v1.0.0** (2024-11-26): Initial Django web application
  - Migrated from desktop PySide6 application
  - Web-based file uploads and report generation
  - 6 out of 7 reports fully implemented
  - Admin interface for master data management

## Credits

Developed for SAP Project System data analysis and reporting automation.
