
import streamlit as st

from utils.auth import (
    create_user,
    delete_user,
    get_all_users,
    get_user_statistics,
    update_user_role,
    update_user_status,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.title("👑 Admin Portal")

st.caption(
    "Manage Construction-AI users, roles, and account access."
)


# ============================================================
# ADMIN SECURITY CHECK
# ============================================================

if not st.session_state.get("authenticated", False):
    st.error("You must be logged in to access this page.")
    st.stop()

if st.session_state.get("user_role") != "Admin":
    st.error("Access denied. Admin privileges are required.")
    st.stop()


# ============================================================
# STATISTICS
# ============================================================

stats = get_user_statistics()

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Users", stats["total"])

with col2:
    st.metric("Admins", stats["admins"])

with col3:
    st.metric("Managers", stats["project_managers"])

with col4:
    st.metric("Safety Officers", stats["safety_officers"])

with col5:
    st.metric("Workers", stats["workers"])


st.divider()


# ============================================================
# TABS
# ============================================================

users_tab, create_tab = st.tabs(
    [
        "👥 User Management",
        "➕ Create User",
    ]
)


# ============================================================
# USER MANAGEMENT
# ============================================================

with users_tab:

    st.subheader("Registered Users")

    users = get_all_users()

    if not users:
        st.info("No users have been registered yet.")

    else:

        for user in users:

            with st.container(border=True):

                col1, col2, col3 = st.columns([2.5, 2, 1.5])

                # ------------------------------------------------
                # USER INFORMATION
                # ------------------------------------------------

                with col1:

                    st.markdown(
                        f"### {user['full_name']}"
                    )

                    st.caption(
                        f"@{user['username']} • {user['email']}"
                    )

                    st.caption(
                        f"Created: {user['created_at']}"
                    )

                    if user["last_login"]:
                        st.caption(
                            f"Last login: {user['last_login']}"
                        )
                    else:
                        st.caption("Last login: Never")

                # ------------------------------------------------
                # ROLE
                # ------------------------------------------------

                with col2:

                    role_options = [
                        "Admin",
                        "Project Manager",
                        "Safety Officer",
                        "Worker",
                    ]

                    current_role_index = role_options.index(
                        user["role"]
                    )

                    new_role = st.selectbox(
                        "Role",
                        role_options,
                        index=current_role_index,
                        key=f"role_{user['id']}",
                    )

                    if new_role != user["role"]:

                        if st.button(
                            "Update Role",
                            key=f"update_role_{user['id']}",
                            use_container_width=True,
                        ):

                            success, message = update_user_role(
                                user["id"],
                                new_role,
                            )

                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)

                # ------------------------------------------------
                # ACCOUNT STATUS
                # ------------------------------------------------

                with col3:

                    if user["is_verified"]:

                        st.success("🟢 Active")

                        if user["id"] != st.session_state["user_id"]:

                            if st.button(
                                "Deactivate",
                                key=f"deactivate_{user['id']}",
                                use_container_width=True,
                            ):

                                success, message = update_user_status(
                                    user["id"],
                                    False,
                                )

                                if success:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)

                    else:

                        st.error("🔴 Inactive")

                        if st.button(
                            "Activate",
                            key=f"activate_{user['id']}",
                            use_container_width=True,
                        ):

                            success, message = update_user_status(
                                user["id"],
                                True,
                            )

                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)

                # ------------------------------------------------
                # DELETE
                # ------------------------------------------------

                if user["id"] != st.session_state["user_id"]:

                    delete_col1, delete_col2 = st.columns(
                        [5, 1]
                    )

                    with delete_col2:

                        if st.button(
                            "🗑️ Delete",
                            key=f"delete_{user['id']}",
                            use_container_width=True,
                        ):

                            success, message = delete_user(
                                user["id"]
                            )

                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)


# ============================================================
# CREATE USER
# ============================================================

with create_tab:

    st.subheader("Create New User")

    st.info(
        "Users created by the Admin can be assigned any supported role."
    )

    with st.form("admin_create_user_form"):

        full_name = st.text_input(
            "Full Name",
            placeholder="Enter full name",
        )

        email = st.text_input(
            "Email",
            placeholder="user@example.com",
        )

        username = st.text_input(
            "Username",
            placeholder="username",
        )

        password = st.text_input(
            "Temporary Password",
            type="password",
            placeholder="Minimum 8 characters",
        )

        role = st.selectbox(
            "Role",
            [
                "Worker",
                "Safety Officer",
                "Project Manager",
                "Admin",
            ],
        )

        submitted = st.form_submit_button(
            "Create User",
            use_container_width=True,
        )

    if submitted:

        success, message = create_user(
            full_name=full_name,
            email=email,
            username=username,
            password=password,
            role=role,
        )

        if success:

            st.success(message)

            st.info(
                f"Account created for {username} "
                f"with role: {role}"
            )

        else:

            st.error(message)