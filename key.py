import secrets
import string

def generate_secret_key(length=32):
    """Generate a cryptographically secure secret key"""
    # Use a combination of letters, digits, and punctuation
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_jwt_secret_key(length=64):
    """Generate a longer JWT secret key"""
    return generate_secret_key(length)

if __name__ == "__main__":
    # Generate different types of secret keys
    flask_secret_key = generate_secret_key()
    jwt_secret_key = generate_jwt_secret_key()
    
    print("=== Flask Secret Key ===")
    print(flask_secret_key)
    print("\n=== JWT Secret Key ===")
    print(jwt_secret_key)
    print("\n=== Copy these to your .env file ===")
    print(f"SECRET_KEY='{flask_secret_key}'")
    print(f"JWT_SECRET_KEY='{jwt_secret_key}'")