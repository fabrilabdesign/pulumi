from pathlib import Path
import subprocess
import shutil
from typing import Tuple

def generate_registry_certs(certs_dir: Path, hostname: str) -> Tuple[Path, Path]:
    """Generate TLS certificates for the registry"""
    certs_dir.mkdir(parents=True, exist_ok=True)
    
    key_path = certs_dir / 'registry.key'
    cert_path = certs_dir / 'registry.crt'
    
    if not key_path.exists() or not cert_path.exists():
        # Generate self-signed certificate
        cmd = [
            'openssl', 'req', '-newkey', 'rsa:4096', '-nodes', '-sha256',
            '-keyout', str(key_path),
            '-x509', '-days', '365',
            '-out', str(cert_path),
            '-subj', f'/C=US/ST=CA/L=SanFrancisco/O=MyCompany/CN={hostname}',
            '-addext', f'subjectAltName = IP:{hostname}'
        ]
        
        subprocess.run(cmd, check=True)
        
        # Copy certificate to Docker certs directory
        docker_certs_dir = Path.home() / '.docker' / 'certs.d' / f'{hostname}:5000'
        docker_certs_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(cert_path, docker_certs_dir / 'ca.crt')
    
    return key_path, cert_path 