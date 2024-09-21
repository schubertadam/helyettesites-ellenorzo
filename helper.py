import os

def load_env(filename: str = '.env'):
    with open(filename) as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue  # Skip comments and blank lines
            key, value = line.split('=', 1)
            value = value.strip('"').strip("'")
            os.environ[key] = value  # Set the value in os.environ