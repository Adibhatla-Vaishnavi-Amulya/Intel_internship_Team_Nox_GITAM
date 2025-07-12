import streamlit as st
import pandas as pd
import re
from pathlib import Path

# Update these paths as needed
CSV_PATHS = {
    'student': r"C:\Users\vaish\Documents\STUDY\INTEL INTERNSHIP\Datasets\Students.csv",
    'teacher': r"C:\Users\vaish\Documents\STUDY\INTEL INTERNSHIP\Datasets\Teachers.csv",
    'admin':   r"C:\Users\vaish\Documents\STUDY\INTEL INTERNSHIP\Datasets\Admins.csv"
}

def get_id_col(role):
    return 'REGISTRATION NUMBER' if role == 'student' else 'EMPLOYEE ID'

def get_account_col():
    return 'ACCOUNT CREATED'

def get_password_col():
    return 'PASSWORD'

def load_users(role):
    path = CSV_PATHS.get(role)
    if not path or not Path(path).exists():
        return None
    try:
        df = pd.read_csv(path)
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

def show_dashboard():
    st.title("Classroom Assistant")
    st.subheader("Choose your role")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Student"):
            st.session_state['role'] = 'student'
            st.session_state['page'] = 'login'
    with col2:
        if st.button("Teacher"):
            st.session_state['role'] = 'teacher'
            st.session_state['page'] = 'login'
    with col3:
        if st.button("Admin"):
            st.session_state['role'] = 'admin'
            st.session_state['page'] = 'login'

def show_login():
    role = st.session_state.get('role', 'student')
    st.title(f"Login ({role.capitalize()})")
    st.info("Enter your username and password to log in.")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        df = load_users(role)
        if df is None:
            st.error("Invalid role or user database not found.")
            return
        id_col = get_id_col(role)
        account_col = get_account_col()
        password_col = get_password_col()
        df[id_col] = df[id_col].astype(str).str.strip()
        user_rows = df[df[id_col] == username.strip()]
        if user_rows.empty:
            st.error("Account not created. Please sign up.")
            return
        user = user_rows.iloc[0]
        if str(user.get(account_col, '')).strip().lower() != 'yes':
            st.error("Account not created. Please sign up.")
            return
        if str(user.get(password_col, '')) != password:
            st.error("Incorrect password.")
            return
        st.success("Login successful!")
        # Here you can redirect to a dashboard or next page if needed

    st.markdown("[Forgot Password?](#)", unsafe_allow_html=True)
    if st.button("Sign Up"):
        st.session_state['page'] = 'signup'

    if st.button("Back to Dashboard"):
        st.session_state['page'] = 'dashboard'

def show_signup():
    role = st.session_state.get('role', 'student')
    st.title(f"Sign Up ({role.capitalize()})")
    st.info("Fill all fields to create a new account. Use a strong password.")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    if st.button("Sign Up"):
        if password != confirm_password:
            st.error("Passwords do not match.")
            return
        df = load_users(role)
        if df is None:
            st.error("Invalid role or user database not found.")
            return
        id_col = get_id_col(role)
        account_col = get_account_col()
        password_col = get_password_col()
        df[id_col] = df[id_col].astype(str).str.strip()
        df['MAIL ID'] = df['MAIL ID'].astype(str).str.strip().str.lower()
        match = (df[id_col] == username.strip()) & (df['MAIL ID'] == email.strip().lower())
        if not match.any():
            st.error("Invalid ID or mail id.")
            return
        idx = df.index[match][0]
        if password_col not in df.columns:
            df[password_col] = ''
        if account_col not in df.columns:
            df[account_col] = 'No'
        if str(df.at[idx, account_col]).strip().lower() == 'yes':
            st.error("Account already created. Please login.")
            return
        if not password_valid(password):
            st.error("Password must be at least 8 characters, with uppercase, lowercase, digit, and special character.")
            return
        df.at[idx, password_col] = password
        df.at[idx, account_col] = 'Yes'
        save_users(df, role)
        st.success("Account created successfully. Please login.")
        st.session_state['page'] = 'login'

    if st.button("Back to Login"):
        st.session_state['page'] = 'login'

def show_forgot_password():
    role = st.session_state.get('role', 'student')
    st.title(f"Forgot Password ({role.capitalize()})")
    st.info("Enter your username and set a new password.")
    username = st.text_input("Username")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm New Password", type="password")
    if st.button("Reset Password"):
        if new_password != confirm_password:
            st.error("Passwords do not match.")
            return
        df = load_users(role)
        if df is None:
            st.error("Invalid role or user database not found.")
            return
        id_col = get_id_col(role)
        account_col = get_account_col()
        password_col = get_password_col()
        df[id_col] = df[id_col].astype(str).str.strip()
        user_rows = df[df[id_col] == username.strip()]
        if user_rows.empty:
            st.error("ID not found.")
            return
        idx = user_rows.index[0]
        if password_col not in df.columns:
            df[password_col] = ''
        if account_col not in df.columns:
            df[account_col] = 'No'
        if str(df.at[idx, account_col]).strip().lower() != 'yes':
            st.error("Account not created. Please sign up first.")
            return
        if not password_valid(new_password):
            st.error("Password must be at least 8 characters, with uppercase, lowercase, digit, and special character.")
            return
        df.at[idx, password_col] = new_password
        save_users(df, role)
        st.success("Password updated successfully. Please login.")
        st.session_state['page'] = 'login'

    if st.button("Back to Login"):
        st.session_state['page'] = 'login'

# Streamlit navigation
if 'page' not in st.session_state:
    st.session_state['page'] = 'dashboard'
if 'role' not in st.session_state:
    st.session_state['role'] = 'student'

if st.session_state['page'] == 'dashboard':
    show_dashboard()
elif st.session_state['page'] == 'login':
    show_login()
elif st.session_state['page'] == 'signup':
    show_signup()
elif st.session_state['page'] == 'forgot_password':
    show_forgot_password()
