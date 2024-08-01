import sqlite3
import hashlib
import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager
from datetime import datetime, timedelta

cookies = EncryptedCookieManager(
    prefix="volta_app/",
    password="your_secret_key_here"  # Replace with a secure secret key
)

def create_users_table():
    conn = sqlite3.connect('stations.sqlite')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(username, password):
    hashed_password = hash_password(password)
    conn = sqlite3.connect('stations.sqlite')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    hashed_password = hash_password(password)
    conn = sqlite3.connect('stations.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def login_page():
    st.title("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login", key="login_button"):
        if verify_user(username, password):
            st.session_state['logged_in'] = True
            st.session_state['current_user'] = username
            cookies['username'] = username
            cookies['expiry'] = (datetime.now() + timedelta(days=7)).isoformat()
            cookies.save()
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid username or password")

def signup_page():
    st.title("Sign Up")
    username = st.text_input("Username", key="signup_username")
    password = st.text_input("Password", type="password", key="signup_password")
    if st.button("Sign Up", key="signup_button"):
        if add_user(username, password):
            st.success("User created successfully! Please log in.")
        else:
            st.error("Username already exists")

def logout():
    st.session_state['logged_in'] = False
    st.session_state['current_user'] = None
    cookies['username'] = None
    cookies['expiry'] = None
    cookies.save()
    st.rerun()

def get_current_user():
    return st.session_state.get('current_user', None)

def check_login_status():
    if cookies.ready():
        if 'username' in cookies and 'expiry' in cookies:
            expiry = datetime.fromisoformat(cookies['expiry'])
            if datetime.now() < expiry:
                st.session_state['logged_in'] = True
                st.session_state['current_user'] = cookies['username']
                return True
    return False
