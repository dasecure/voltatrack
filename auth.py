import sqlite3
import hashlib
import streamlit as st

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
            st.success("Logged in successfully!")
            st.experimental_rerun()
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
    st.experimental_rerun()

def get_current_user():
    return st.session_state.get('current_user', None)
