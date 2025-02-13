from pathlib import Path
import subprocess
import secrets
import string

def generate_htpasswd(auth_dir: Path, username: str) -> str:
    """Generate htpasswd file and return the generated password"""
    auth_dir.mkdir(parents=True, exist_ok=True)
    htpasswd_path = auth_dir / 'htpasswd'
    
    # Generate a random password
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for _ in range(16))
    
    # Create htpasswd file using httpd image
    cmd = [
        'docker', 'run', '--rm',
        '--entrypoint', 'htpasswd',
        'httpd:2',
        '-Bbn', username, password
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    htpasswd_path.write_text(result.stdout)
    
    return password 