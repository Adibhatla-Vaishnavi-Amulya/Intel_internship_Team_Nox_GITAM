from flask import Flask, render_template, request, jsonify, session, send_from_directory
import pandas as pd
import re
import os
from werkzeug.utils import secure_filename

# For chatbot
from transformers import AutoTokenizer
from optimum.intel.openvino import OVModelForCausalLM
import PyPDF2

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'your_secret_key_here'

CSV_PATHS = {
    'student': r"C:\Users\HP\Desktop\intelu\INTEL_INTERNSHIP\Datasets\Students.csv",
    'teacher': r"C:\Users\HP\Desktop\intelu\INTEL_INTERNSHIP\Datasets\Teachers.csv",
    'admin':   r"C:\Users\HP\Desktop\intelu\INTEL_INTERNSHIP\Datasets\Admins.csv"
}
DATASETS_FOLDER = r"C:\Users\HP\Desktop\intelu\INTEL_INTERNSHIP\Datasets"
MAPPING_CSV = os.path.join(DATASETS_FOLDER, "Student_Teacher_Subject_Mapping.csv")
MODULES_FOLDER = DATASETS_FOLDER  # e.g., Datasets/dbms/module1.pdf

# Load model and tokenizer globally (once on app start)
model_path = r"C:\Users\HP\Desktop\intelu\mistral-7b-instruct-v0.1-int8-ov"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = OVModelForCausalLM.from_pretrained(model_path)

def get_id_col(role):
    return 'REGISTRATION NUMBER' if role == 'student' else 'EMPLOYEE ID'

def get_account_col():
    return 'ACCOUNT CREATED'

def get_password_col():
    return 'PASSWORD'

def load_users(role):
    path = CSV_PATHS.get(role)
    if not path:
        return None
    try:
        df = pd.read_csv(path)
        df = df.fillna('')
        df.columns = [col.strip().upper() for col in df.columns]
        return df
    except Exception:
        if role == 'student':
            return pd.DataFrame(columns=[
                'BRANCH', 'DEPARTMENT', 'SCHOOL', 'REGISTRATION NUMBER', 'NAME', 'MAIL ID', 'SPECIALIZATION', 'YEAR OF STUDY',
                'ACCOUNT CREATED', 'PASSWORD'
            ])
        else:
            return pd.DataFrame(columns=[
                'BRANCH', 'DEPARTMENT', 'SCHOOL', 'EMPLOYEE ID', 'NAME', 'MAIL ID', 'DESIGNATION',
                'ACCOUNT CREATED', 'PASSWORD'
            ])

def save_users(df, role):
    path = CSV_PATHS.get(role)
    if path:
        df.to_csv(path, index=False)

def password_valid(password):
    return (len(password) >= 8 and
            re.search(r'[A-Z]', password) and
            re.search(r'[a-z]', password) and
            re.search(r'\d', password) and
            re.search(r'[^A-Za-z0-9]', password))

@app.route('/')
def dashboard():
    return render_template('Dashboard.html')

@app.route('/login')
def login():
    return render_template('Login.html')

@app.route('/signup')
def signup():
    return render_template('SignUp.html')

@app.route('/forgot-password')
def forgot_password():
    mode = request.args.get('mode', 'forgot')
    role = request.args.get('role', 'student')
    return render_template('Forgot Password.html', mode=mode, role=role)

@app.route('/<role>/login', methods=['POST'])
def role_login(role):
    df = load_users(role)
    if df is None:
        return jsonify({'success': False, 'message': 'Invalid role.'})

    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')

    id_col = get_id_col(role)
    account_col = get_account_col()
    password_col = get_password_col()

    df[id_col] = df[id_col].astype(str).str.strip()
    user_rows = df[df[id_col] == username]
    if user_rows.empty:
        return jsonify({'success': False, 'message': 'Account not created. Please sign up.'})

    user = user_rows.iloc[0]
    if str(user.get(account_col, '')).strip().lower() != 'yes':
        return jsonify({'success': False, 'message': 'Account not created. Please sign up.'})

    if str(user.get(password_col, '')) != password:
        return jsonify({'success': False, 'message': 'Incorrect password.'})

    session['role'] = role
    session['username'] = username
    session['name'] = user.get('NAME', username)

    return jsonify({'success': True, 'message': 'Login successful.'})

@app.route('/<role>/signup', methods=['POST'])
def role_signup(role):
    df = load_users(role)
    if df is None:
        return jsonify({'success': False, 'message': 'Invalid role.'})

    data = request.json
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    id_col = get_id_col(role)
    account_col = get_account_col()
    password_col = get_password_col()

    df[id_col] = df[id_col].astype(str).str.strip()
    df['MAIL ID'] = df['MAIL ID'].astype(str).str.strip().str.lower()

    match = (df[id_col] == username) & (df['MAIL ID'] == email)
    if not match.any():
        return jsonify({'success': False, 'message': 'Invalid ID or mail ID.'})

    idx = df.index[match][0]

    if password_col not in df.columns:
        df[password_col] = ''
    else:
        df[password_col] = df[password_col].astype(str)
    if account_col not in df.columns:
        df[account_col] = 'No'
    else:
        df[account_col] = df[account_col].astype(str)

    if str(df.at[idx, account_col]).strip().lower() == 'yes':
        return jsonify({'success': False, 'message': 'Account already created. Please login.'})

    if not password_valid(password):
        return jsonify({'success': False, 'message': 'Password must be at least 8 characters, with uppercase, lowercase, digit, and special character.'})

    df.at[idx, password_col] = password
    df.at[idx, account_col] = 'Yes'
    save_users(df, role)
    return jsonify({'success': True, 'message': 'Account created successfully. Please login.'})

@app.route('/<role>/reset-password', methods=['POST'])
def role_reset_password(role):
    df = load_users(role)
    if df is None:
        return jsonify({'success': False, 'message': 'Invalid role.'})

    data = request.json
    username = data.get('username', '').strip()
    new_password = data.get('new_password', '')

    id_col = get_id_col(role)
    account_col = get_account_col()
    password_col = get_password_col()

    df[id_col] = df[id_col].astype(str).str.strip()
    user_rows = df[df[id_col] == username]
    if user_rows.empty:
        return jsonify({'success': False, 'message': 'ID not found.'})

    idx = user_rows.index[0]

    if password_col not in df.columns:
        df[password_col] = ''
    else:
        df[password_col] = df[password_col].astype(str)
    if account_col not in df.columns:
        df[account_col] = 'No'
    else:
        df[account_col] = df[account_col].astype(str)

    if str(df.at[idx, account_col]).strip().lower() != 'yes':
        return jsonify({'success': False, 'message': 'Account not created. Please sign up first.'})

    if not password_valid(new_password):
        return jsonify({'success': False, 'message': 'Password must be at least 8 characters, with uppercase, lowercase, digit, and special character.'})

    df.at[idx, password_col] = new_password
    save_users(df, role)
    return jsonify({'success': True, 'message': 'Password updated successfully. Please login.'})

@app.route('/profile', methods=['POST'])
def profile():
    role = session.get('role')
    username = session.get('username')
    if not role or not username:
        return jsonify({'success': False, 'message': 'Not logged in.'}), 401

    df = load_users(role)
    if df is None:
        return jsonify({'success': False, 'message': 'Invalid role.'}), 400

    id_col = get_id_col(role)
    df[id_col] = df[id_col].astype(str).str.strip()
    user_rows = df[df[id_col] == username]
    if user_rows.empty:
        return jsonify({'success': False, 'message': 'User not found.'}), 404

    user = user_rows.iloc[0]
    exclude = {'ACCOUNT CREATED', 'PASSWORD'}

    ordered_profile = []
    for col in df.columns:
        if col not in exclude:
            value = user[col]
            if hasattr(value, 'item'):
                value = value.item()
            ordered_profile.append({'key': col, 'value': value})

    return jsonify({'success': True, 'profile': ordered_profile})

@app.route('/admin/list-csvs', methods=['GET'])
def list_csvs():
    files = [f for f in os.listdir(DATASETS_FOLDER) if f.lower().endswith('.csv')]
    return jsonify({'success': True, 'files': files})

@app.route('/admin/get-csv', methods=['POST'])
def get_csv():
    data = request.json
    filename = data.get('filename')
    if not filename or not filename.lower().endswith('.csv'):
        return jsonify({'success': False, 'message': 'Invalid filename.'}), 400
    filepath = os.path.join(DATASETS_FOLDER, filename)
    if not os.path.isfile(filepath):
        return jsonify({'success': False, 'message': 'File not found.'}), 404
    try:
        df = pd.read_csv(filepath)
        df = df.fillna('')
        data = df.to_dict(orient='records')
        columns = list(df.columns)
        return jsonify({'success': True, 'columns': columns, 'data': data})
    except Exception as e:
        print("Error reading CSV:", e)
        return jsonify({'success': False, 'message': str(e)}), 500

# --- TEACHER: Courses, Students, PDF Uploads, Progress ---
@app.route('/teacher/courses-data')
def teacher_courses_data():
    teacher_id = session.get('username')
    df = pd.read_csv(MAPPING_CSV)
    subjects = sorted(df[df['EMPLOYEE ID'].astype(str) == str(teacher_id)]['SUBJECT'].unique())
    return jsonify({'subjects': subjects})

@app.route('/teacher/upload-module-pdf', methods=['POST'])
def upload_module_pdf():
    teacher_id = session.get('username')
    subject = request.form['subject']
    module_number = request.form['module_number']
    file = request.files['pdf']
    df = pd.read_csv(MAPPING_CSV)
    allowed_subjects = set(df[df['EMPLOYEE ID'].astype(str) == str(teacher_id)]['SUBJECT'].unique())
    if subject not in allowed_subjects:
        return jsonify({'success': False, 'message': 'Not allowed'}), 403
    subject_folder = os.path.join(MODULES_FOLDER, subject.replace(" ", "_").lower())
    os.makedirs(subject_folder, exist_ok=True)
    filename = secure_filename(f"module{module_number}.pdf")
    file.save(os.path.join(subject_folder, filename))
    return jsonify({'success': True, 'message': 'PDF uploaded'})

@app.route('/teacher/list-module-pdfs', methods=['GET'])
def list_module_pdfs():
    subject = request.args.get('subject')
    subject_folder = os.path.join(MODULES_FOLDER, subject.replace(" ", "_").lower())
    files = []
    if os.path.exists(subject_folder):
        files = [f for f in sorted(os.listdir(subject_folder)) if f.lower().endswith('.pdf')]
    return jsonify({'files': files})

@app.route('/teacher/monitor-student-progress', methods=['GET'])
def monitor_student_progress():
    teacher_id = session.get('username')
    df = pd.read_csv(MAPPING_CSV)
    filtered = df[df['EMPLOYEE ID'].astype(str) == str(teacher_id)]
    return filtered.to_json(orient='records')

# --- STUDENT: Courses, Module PDFs, Progress ---
@app.route('/student/courses-data')
def student_courses_data():
    student_id = session.get('username')
    df = pd.read_csv(MAPPING_CSV)
    subjects = sorted(df[df['REGISTRATION NUMBER'].astype(str) == str(student_id)]['SUBJECT'].unique())
    return jsonify({'subjects': subjects})

@app.route('/student/list-module-pdfs', methods=['GET'])
def student_list_module_pdfs():
    subject = request.args.get('subject')
    subject_folder = os.path.join(MODULES_FOLDER, subject.replace(" ", "_").lower())
    files = []
    if os.path.exists(subject_folder):
        files = [f for f in sorted(os.listdir(subject_folder)) if f.lower().endswith('.pdf')]
    return jsonify({'files': files})

@app.route('/student/download-pdf', methods=['GET'])
def student_download_pdf():
    subject = request.args.get('subject')
    filename = request.args.get('filename')
    subject_folder = os.path.join(MODULES_FOLDER, subject.replace(" ", "_").lower())
    return send_from_directory(subject_folder, filename, as_attachment=True)

@app.route('/student/monitor-progress', methods=['GET'])
def student_monitor_progress():
    student_id = session.get('username')
    df = pd.read_csv(MAPPING_CSV)
    filtered = df[df['REGISTRATION NUMBER'].astype(str) == str(student_id)]
    return filtered.to_json(orient='records')

# --- STUDENT: Chatbot for Module ---
@app.route('/student/chatbot', methods=['POST'])
def student_chatbot():
    data = request.json
    subject = data['subject']
    filename = data['filename']
    prompt = data['prompt']
    word_limit = int(data.get('word_limit', 100))

    subject_folder = os.path.join(MODULES_FOLDER, subject.replace(" ", "_").lower())
    pdf_path = os.path.join(subject_folder, filename)
    if not os.path.exists(pdf_path):
        return jsonify({'success': False, 'message': 'PDF not found.'})

    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
        pdf_text = text.strip()[:1000]
    except Exception as e:
        return jsonify({'success': False, 'message': f'PDF extraction error: {e}'})

    full_prompt = (f"<s>[INST] Based on the following document content, answer the question in {word_limit} words or less:\n\n"
                   f"{pdf_text}\n\nQuestion: {prompt} [/INST]")
    inputs = tokenizer(full_prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=int(word_limit*1.5), pad_token_id=tokenizer.eos_token_id)
    response = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
    prompt_prefix = full_prompt.replace("<s>", "").strip()
    clean_response = response.replace(prompt_prefix, "").strip()
    return jsonify({'success': True, 'response': clean_response})
@app.route('/student/mark-module-complete', methods=['POST'])
def mark_module_complete():
    data = request.json
    student_id = session.get('username')
    subject = data['subject']
    module_number = data['module_number']
    df = pd.read_csv(MAPPING_CSV)
    idx = df[(df['REGISTRATION NUMBER'].astype(str) == str(student_id)) & (df['SUBJECT'] == subject)].index
    module_col = f'MODULE - {int(module_number):02d}'  # Updated format
    if not idx.empty and module_col in df.columns:
        df.at[idx[0], module_col] = 'Yes'
        df.to_csv(MAPPING_CSV, index=False)
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Entry not found or invalid module.'}), 404
    
    
@app.route('/student/interface')
def student_interface():
    name = session.get('name', 'Student')
    return render_template('Student Interface.html', name=name)

@app.route('/teacher/interface')
def teacher_interface():
    name = session.get('name', 'Teacher')
    return render_template('Teacher Interface.html', name=name)

@app.route('/admin/interface')
def admin_interface():
    name = session.get('name', 'Admin')
    return render_template('Admin Interface.html', name=name)

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)