from flask import Flask, render_template, request, redirect, url_for, flash, session
import psycopg2
from supabase import create_client, Client

from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__,
            template_folder="../frontend/templates",
            static_folder="../frontend/static")
app.secret_key = "student_project_secret_key"

DB_HOST = os.getenv("SUPABASE_DB_HOST")
DB_NAME = os.getenv("SUPABASE_DB_NAME", "postgres")
DB_USER = os.getenv("SUPABASE_DB_USER", "postgres")
DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD")
DB_PORT = os.getenv("SUPABASE_DB_PORT", "5432")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT,
        sslmode="require"
    )

    
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, role FROM users WHERE email = %s AND password = %s", (email, password))
    user = cur.fetchone()
    cur.close()
    conn.close()
    
    if user:
        session['user_id'] = user[0]
        session['user_name'] = user[1]
        session['user_email'] = user[2]
        session['user_role'] = user[3]
        return redirect(url_for('dashboard'))
    
    flash("Error: Invalid email or password credentials.")
    return redirect(url_for('home'))

@app.route('/signup', methods=['POST'])
def signup():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    if password != confirm_password:
        flash("Error: Passwords do not match.")
        return redirect(url_for('home'))
        
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, 'Employee')", (name, email, password))
        conn.commit()
        cur.close()
        conn.close()
        flash("Registration Successful! Please sign in below.")
    except psycopg2.IntegrityError:
        flash("Error: This email address is already registered.")
        
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    """The central traffic controller routing users based on Role access."""
    if 'user_id' not in session:
        return redirect(url_for('home'))
        
    role = session.get('user_role')
    user_id = session.get('user_id')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # --- IF LOGGED IN USER IS AN ADMIN ---
    if role == 'Admin':
        cur.execute("SELECT COUNT(*) FROM users WHERE role = 'Manager'")
        total_m = cur.fetchone()[0]
        
        # Count all production roles as employees combined
        cur.execute("SELECT COUNT(*) FROM users WHERE role NOT IN ('Admin', 'Manager')")
        total_e = cur.fetchone()[0]
        
        # Display all system user assets under the primary Admin control pane ledger
        cur.execute("SELECT id, name, email, role FROM users WHERE role != 'Admin'")
        managers_list = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return render_template('dashboard_admin.html', 
                               total_managers=total_m, 
                               total_employees=total_e,
                               total_projects=12, 
                               delayed_projects=2,
                               managers=managers_list)
        
    # --- IF LOGGED IN USER IS A MANAGER ---
    elif role == 'Manager':
        total_p = 5
        active_p = 3
        pending_t = 8
        completed_t = 12
        total_e = 6
        
        projects_data = [
            (10, "Cloud Platform Migration", "Active", "2026-01-10", "2026-08-15", 70),
            (11, "Enterprise IAM Lifecycle", "Active", "2026-03-01", "2026-12-01", 35)
        ]
        
        tasks_data = [
            (501, "Configure Postgres Cluster Routing", "Alex Green", "High", "In-Progress", "2026-06-25"),
            (502, "Draft IAM Security Configurations", "Sarah Jenkins", "Medium", "Open", "2026-07-02")
        ]
        
        cur.execute("SELECT id, name, email, role FROM users WHERE created_by = %s", (user_id,))
        db_team = cur.fetchall()
        
        team_members_list = []
        for member in db_team:
            team_members_list.append((member[0], member[1], member[2], "Assigned Project", 2))
            
        operations_data = [
            (9901, "Staging Pipeline Interrupted", "High", "Investigating", "2026-06-16")
        ]
        
        cur.close()
        conn.close()
        
        return render_template('dashboard_manager.html',
                               total_projects=total_p,
                               active_projects=active_p,
                               pending_tasks=pending_t,
                               completed_tasks=completed_t,
                               total_employees=total_e,
                               projects=projects_data,
                               tasks=tasks_data,
                               team_members=team_members_list,
                               operations=operations_data)
        
    # --- IF LOGGED IN USER IS A FUNCTIONAL INDIVIDUAL CONTRIBUTOR ---
    elif role in ['Employee', 'Developer', 'QA Tester', 'DevOps']:
        assigned_p_count = 1
        total_t_count = 3
        pending_t_count = 2
        completed_t_count = 1
        overdue_t_count = 0
        
        assigned_projects = [
            (10, "Cloud Platform Migration", "Jane Smith", "Active", "2026-08-15", 70)
        ]
        
        employee_tasks = [
            (501, "Configure Postgres Cluster Routing", "Cloud Platform Migration", "High", "In Progress", "2026-06-25"),
            (503, "Run Verification Diagnostics Tests", "Cloud Platform Migration", "Low", "Pending", "2026-07-10")
        ]
        
        employee_operations = [
            (9902, "Staging Framework Timeout Error", "Medium", "Open", "2026-06-17")
        ]
        
        cur.close()
        conn.close()
        
        return render_template('dashboard_employee.html',
                               assigned_projects=assigned_p_count,
                               total_tasks=total_t_count,
                               pending_tasks=pending_t_count,
                               completed_tasks=completed_t_count,
                               overdue_tasks=overdue_t_count,
                               projects=assigned_projects,
                               tasks=employee_tasks,
                               operations=employee_operations)
    
    else:
        cur.close()
        conn.close()
        return redirect(url_for('logout'))

# ==========================================
# SECURE ROLE-BASED ACTION REQUEST HANDLERS
# ==========================================

# --- RENAME & UPGRADE: DYNAMIC USER PROVISIONING ---
@app.route('/admin/add-user', methods=['POST'])
def add_user():
    if session.get('user_role') != 'Admin':
        return "Unauthorized Access", 403
        
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    assigned_role = request.form.get('role') # Grabs Developer, DevOps, QA Tester, or Manager
    
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (name, email, password, role, created_by) VALUES (%s, %s, %s, %s, %s)", 
                    (name, email, password, assigned_role, session['user_id']))
        conn.commit()
        flash(f"Successfully added {assigned_role}: {name}")
    except psycopg2.IntegrityError:
        flash("Error: That user profile email address already exists.")
    cur.close()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/admin/disable-manager/<int:manager_id>', methods=['POST'])
def disable_manager(manager_id):
    if session.get('user_role') != 'Admin':
        return "Unauthorized Access", 403
        
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET password = 'DISABLED_ACCOUNT_LOCKED' WHERE id = %s AND role != 'Admin'", (manager_id,))
    conn.commit()
    cur.close()
    conn.close()
    
    flash("User credentials disabled successfully.")
    return redirect(url_for('dashboard'))

@app.route('/admin/remove-manager/<int:manager_id>', methods=['POST'])
def remove_manager(manager_id):
    if session.get('user_role') != 'Admin':
        return "Unauthorized Access", 403
        
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM users WHERE id = %s AND role != 'Admin'", (manager_id,))
        conn.commit()
        flash("User completely removed from system ledger.")
    except psycopg2.Error:
        flash("Error: Could not remove user account. Check for active database row dependencies.")
    cur.close()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/manager/add-staff', methods=['POST'])
def add_staff():
    if session.get('user_role') != 'Manager':
        return "Unauthorized Access", 403
        
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    assigned_role = request.form.get('role')
    
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (name, email, password, role, created_by) VALUES (%s, %s, %s, %s, %s)", 
                    (name, email, password, assigned_role, session['user_id']))
        conn.commit()
        flash(f"Successfully added {assigned_role}: {name}")
    except psycopg2.IntegrityError:
        flash("Error: Account email already exists.")
    cur.close()
    conn.close()
    return redirect(url_for('dashboard'))

# ==========================================
# EMPLOYEE ACTION HANDLERS
# ==========================================

@app.route('/employee/update-task-status', methods=['POST'])
def update_task_status():
    if session.get('user_role') not in ['Employee', 'Developer', 'QA Tester', 'DevOps']:
        return "Unauthorized Access", 403
    task_id = request.form.get('task_id')
    new_status = request.form.get('status')
    flash(f"Success: Task #{task_id} status updated to '{new_status}'")
    return redirect(url_for('dashboard'))

@app.route('/employee/complete-task', methods=['POST'])
def complete_task():
    if session.get('user_role') not in ['Employee', 'Developer', 'QA Tester', 'DevOps']:
        return "Unauthorized Access", 403
    task_id = request.form.get('task_id')
    flash(f"Success: Task #{task_id} marked as completed.")
    return redirect(url_for('dashboard'))

@app.route('/employee/report-issue', methods=['POST'])
def employee_report_issue():
    if session.get('user_role') not in ['Employee', 'Developer', 'QA Tester', 'DevOps']:
        return "Unauthorized Access", 403
    title = request.form.get('title')
    severity = request.form.get('severity')
    flash(f"Incident Logged: '{title}' registered under severity '{severity}'")
    return redirect(url_for('dashboard'))

@app.route('/employee/add-comment', methods=['POST'])
def employee_add_comment():
    if session.get('user_role') not in ['Employee', 'Developer', 'QA Tester', 'DevOps']:
        return "Unauthorized Access", 403
    flash("Progress update note attached to task overview timeline.")
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
