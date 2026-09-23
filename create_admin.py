from utils.auth import initialize_users_table, create_user


initialize_users_table()

success, message = create_user(
    full_name="System Administrator",
    email="admin@constructai.local",
    username="admin",
    password="Admin@1234",
    role="Admin",
)

print(message)