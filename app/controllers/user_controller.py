from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.user import User
from app.database import db
from werkzeug.security import generate_password_hash

user_bp = Blueprint('user', __name__)


@user_bp.route('/users')
@login_required
def users_list():
    # Only main user can view user list
    if current_user.role != 'main':
        flash('Access denied. Only main user can manage users.', 'error')
        return redirect(url_for('voter.search'))
    
    users = User.query.all()
    return render_template('user/list.html', users=users)


@user_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
def create_user():
    # Only main user can create users
    if current_user.role != 'main':
        flash('Access denied. Only main user can create users.', 'error')
        return redirect(url_for('voter.search'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        
        # Validate inputs
        if not username or not password or not role:
            flash('All fields are required', 'error')
            return render_template('user/create.html')
        
        if role not in ['main', 'sub']:
            flash('Invalid role selected', 'error')
            return render_template('user/create.html')
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('user/create.html')
        
        # Create new user
        user = User(
            username=username,
            role=role
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'User {username} created successfully', 'success')
        return redirect(url_for('user.users_list'))
    
    return render_template('user/create.html')


@user_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    # Only main user can edit users
    if current_user.role != 'main':
        flash('Access denied. Only main user can edit users.', 'error')
        return redirect(url_for('voter.search'))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent editing the main user's role
    if user.id == current_user.id and user.role == 'main':
        is_self_edit = True
    else:
        is_self_edit = False
    
    if request.method == 'POST':
        # Handle password change
        new_password = request.form.get('password')
        if new_password:
            user.set_password(new_password)
        
        # Handle deactivation (only for sub users)
        if not is_self_edit and user.role != 'main':
            is_active = request.form.get('is_active') == 'on'
            user.is_active = is_active
        
        db.session.commit()
        flash(f'User {user.username} updated successfully', 'success')
        return redirect(url_for('user.users_list'))
    
    return render_template('user/edit.html', user=user, is_self_edit=is_self_edit)


@user_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    # Only main user can delete users
    if current_user.role != 'main':
        flash('Access denied. Only main user can delete users.', 'error')
        return redirect(url_for('voter.search'))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting the main user
    if user.role == 'main' and User.query.filter_by(role='main').count() <= 1:
        flash('Cannot delete the only main user', 'error')
        return redirect(url_for('user.users_list'))
    
    # Don't allow deleting self
    if user.id == current_user.id:
        flash('Cannot delete yourself', 'error')
        return redirect(url_for('user.users_list'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {user.username} deleted successfully', 'success')
    return redirect(url_for('user.users_list'))