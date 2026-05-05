import os
from pathlib import Path

def load_dotenv_file(dotenv_path=None):
    """
    Load environment variables from a .env file.
    If dotenv_path is not provided, looks for .env in the current directory.
    """
    if dotenv_path is None:
        dotenv_path = Path.cwd() / ".env"
    
    if not dotenv_path.exists():
        return
    
    with open(dotenv_path) as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue
            # Parse KEY=VALUE
            if "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

def get_env(key, default=None):
    """Get an environment variable, with optional default."""
    return os.environ.get(key, default)
