"""
Route handlers for the Task Tracker application.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from models import db, Task

main = Blueprint('main', __name__)

# Valid status options for tasks
VALID_STATUSES = ['Pending', 'In Progress', 'Completed']


@main.route('/')
def index():
    """Display all tasks on the dashboard."""
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return render_template('index.html', tasks=tasks)


@main.route('/create', methods=['GET', 'POST'])
def create():
    """Create a new task."""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        status = request.form.get('status', 'Pending')

        # Validation
        errors = []
        if not title:
            errors.append('Title is required and cannot be empty.')
        if len(title) > 200:
            errors.append('Title must be 200 characters or less.')
        if status not in VALID_STATUSES:
            errors.append('Invalid status selected.')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('create.html',
                                 title=title,
                                 description=description,
                                 status=status,
                                 statuses=VALID_STATUSES)

        # Create new task
        try:
            new_task = Task(
                title=title,
                description=description if description else None,
                status=status
            )
            db.session.add(new_task)
            db.session.commit()
            flash(f'Task "{title}" created successfully!', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating the task. Please try again.', 'error')
            return render_template('create.html',
                                 title=title,
                                 description=description,
                                 status=status,
                                 statuses=VALID_STATUSES)

    return render_template('create.html', statuses=VALID_STATUSES)


@main.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit(task_id):
    """Edit an existing task."""
    task = Task.query.get_or_404(task_id)

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        status = request.form.get('status', 'Pending')

        # Validation
        errors = []
        if not title:
            errors.append('Title is required and cannot be empty.')
        if len(title) > 200:
            errors.append('Title must be 200 characters or less.')
        if status not in VALID_STATUSES:
            errors.append('Invalid status selected.')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('edit.html',
                                 task=task,
                                 title=title,
                                 description=description,
                                 status=status,
                                 statuses=VALID_STATUSES)

        # Update task
        try:
            task.title = title
            task.description = description if description else None
            task.status = status
            db.session.commit()
            flash(f'Task "{title}" updated successfully!', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the task. Please try again.', 'error')
            return render_template('edit.html',
                                 task=task,
                                 statuses=VALID_STATUSES)

    return render_template('edit.html', task=task, statuses=VALID_STATUSES)


@main.route('/delete/<int:task_id>', methods=['POST'])
def delete(task_id):
    """Delete a task."""
    task = Task.query.get_or_404(task_id)

    try:
        task_title = task.title
        db.session.delete(task)
        db.session.commit()
        flash(f'Task "{task_title}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the task. Please try again.', 'error')

    return redirect(url_for('main.index'))


@main.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template('404.html'), 404
