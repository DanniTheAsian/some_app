from backend.model.user import User

u = User()
print("Testing user lookup...")
print(u.get_by_email("test@test.com"))
