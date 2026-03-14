# Project Task Tracker

A complete, functional web application for managing project tasks built with Python, Flask, and Jinja2 using Server-Side Rendering. No frontend JavaScript is used - the interface is pure HTML and CSS.

## Features

- **Complete CRUD Operations**: Create, Read, Update, and Delete tasks
- **Persistent Storage**: SQLite database with Flask-SQLAlchemy
- **Task Management**: Track tasks with title, description, and status (Pending, In Progress, Completed)
- **Validation**: Backend validation with user-friendly error messages
- **Flash Messages**: Success and error notifications via Server-Side Rendering
- **Error Handling**: Proper 404 pages and error recovery
- **Clean UI**: Modern interface using Pico.css classless framework
- **Modular Architecture**: Organized code structure ready for future enhancements

## Project Structure

```
project/
├── app.py                  # Main Flask application and configuration
├── models.py               # Database models (Task model)
├── routes.py               # Route handlers for all CRUD operations
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── tasks.db               # SQLite database (created automatically)
└── templates/             # Jinja2 templates
    ├── base.html          # Base template with layout and styling
    ├── index.html         # Dashboard showing all tasks
    ├── create.html        # Form to create new task
    ├── edit.html          # Form to edit existing task
    └── 404.html           # Custom 404 error page
```

## Technology Stack

- **Backend**: Python 3.8+
- **Web Framework**: Flask 3.0.0
- **ORM**: Flask-SQLAlchemy 3.1.1
- **Database**: SQLite
- **Templating**: Jinja2 (included with Flask)
- **Styling**: Pico.css (via CDN)

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Step 1: Clone or Download the Project

If you received this as a zip file, extract it. Otherwise, navigate to the project directory:

```bash
cd project
```

### Step 2: Create a Virtual Environment

Creating a virtual environment keeps your project dependencies isolated:

**On macOS/Linux:**
```bash
python3 -m venv venv
```

**On Windows:**
```bash
python -m venv venv
```

### Step 3: Activate the Virtual Environment

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**On Windows (Command Prompt):**
```bash
venv\Scripts\activate
```

**On Windows (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```

You should see `(venv)` appear at the beginning of your terminal prompt.

### Step 4: Install Dependencies

With the virtual environment activated, install the required packages:

```bash
pip install -r requirements.txt
```

This will install Flask and Flask-SQLAlchemy.

### Step 5: Initialize the Database

The database is automatically initialized when you first run the application. The `tasks.db` file will be created in the project root directory.

### Step 6: Run the Application

Start the Flask development server:

```bash
python app.py
```

You should see output similar to:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://0.0.0.0:5000
```

### Step 7: Access the Application

Open your web browser and navigate to:

```
http://localhost:5000
```

You should see the Task Tracker dashboard!

## Usage Guide

### Creating a Task

1. Click the "New Task" button on the dashboard
2. Fill in the task title (required)
3. Optionally add a description
4. Select a status (Pending, In Progress, or Completed)
5. Click "Create Task"

### Viewing Tasks

All tasks are displayed on the main dashboard at `http://localhost:5000`. Tasks are shown with:
- Title and status badge
- Description (if provided)
- Edit and Delete buttons

### Editing a Task

1. Click the "Edit" button on any task card
2. Modify the title, description, or status
3. Click "Update Task" to save changes
4. Click "Cancel" to discard changes

### Deleting a Task

1. Click the "Delete" button on any task card
2. The task will be immediately deleted
3. A confirmation message will be displayed

### Validation

The application includes backend validation:
- Task title is required and cannot be empty
- Task title must be 200 characters or less
- Status must be one of the valid options
- Error messages are displayed via flash messages

## Development Notes

### Modular Architecture

The codebase is organized following best practices:

- **models.py**: Contains the Task model and database configuration
- **routes.py**: Handles all HTTP routes and business logic
- **app.py**: Application factory and configuration
- **templates/**: Jinja2 templates with inheritance

This structure makes the code:
- Easy to test
- Simple to maintain
- Ready for integration with external APIs
- Prepared for future enhancements

### Database Schema

The Task model includes:
```python
- id: Integer (Primary Key)
- title: String(200) (Required)
- description: Text (Optional)
- status: String(50) (Default: 'Pending')
- created_at: DateTime (Auto-generated)
- updated_at: DateTime (Auto-updated)
```

### Future Enhancement Ideas

- User authentication and multi-user support
- Task filtering and search functionality
- Task priorities and due dates
- Task categories or projects
- Export tasks to CSV or JSON
- REST API endpoints
- Unit and integration tests

## Troubleshooting

### Database Issues

If you encounter database errors, delete the `tasks.db` file and restart the application. The database will be recreated automatically.

```bash
rm tasks.db  # On macOS/Linux
del tasks.db  # On Windows
python app.py
```

### Port Already in Use

If port 5000 is already in use, you can change the port in `app.py`:

```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change to any available port
```

### Virtual Environment Issues

Make sure you've activated the virtual environment before running the application. You should see `(venv)` in your terminal prompt.

## Stopping the Application

To stop the Flask development server, press `Ctrl+C` in the terminal.

To deactivate the virtual environment:

```bash
deactivate
```

## Security Notes

- The application uses a default SECRET_KEY for development
- For production deployment, set a secure SECRET_KEY environment variable
- Never commit sensitive credentials to version control
- SQLite is suitable for development; consider PostgreSQL for production

## License

This project is provided as-is for educational and development purposes.

## Support

For issues or questions, please review the code comments and this README. The codebase is designed to be self-documenting with clear function and variable names.
