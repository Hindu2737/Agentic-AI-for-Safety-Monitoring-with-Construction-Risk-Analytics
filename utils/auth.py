import hmac
import streamlit as st


# ============================================================
# DEMO USERS
# ============================================================

USERS = {
    "admin": {
        "password": "admin123",
        "role": "Admin",
    },
    "manager": {
        "password": "manager123",
        "role": "Project Manager",
    },
    "safety": {
        "password": "safety123",
        "role": "Safety Officer",
    },
    "worker": {
        "password": "worker123",
        "role": "Worker",
    },
}


# ============================================================
# LOGIN
# ============================================================

def verify_password(username, password):
    user = USERS.get(username)

    if not user:
        return False

    return hmac.compare_digest(
        user["password"],
        password,
    )


def login_user(username, password):
    if verify_password(username, password):
        st.session_state["authenticated"] = True
        st.session_state["username"] = username
        st.session_state["user_role"] = USERS[username]["role"]

        return True

    return False


# ============================================================
# LOGOUT
# ============================================================

def logout_user():
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.session_state["user_role"] = None


# ============================================================
# AUTHENTICATION STATUS
# ============================================================

def is_authenticated():
    return st.session_state.get("authenticated", False)


# ============================================================
# ROLE CHECK
# ============================================================

def has_role(allowed_roles):
    role = st.session_state.get("user_role")

    return role in allowed_roles