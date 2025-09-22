#!/usr/bin/env python3
"""
Setup script for Click2Endpoint
Ensures virtual environment is created and dependencies are installed
"""
import os
import sys
import subprocess
from pathlib import Path

def setup_venv():
    """Create and setup virtual environment"""
    
    # Determine project root and venv location
    project_root = Path(__file__).parent
    venv_path = project_root / '.venv'
    streamlit_venv_path = project_root / 'streamlit_app' / '.venv'
    
    print(f"Setting up Click2Endpoint...")
    print(f"Project root: {project_root}")
    
    # Check if we need to create venv
    if not venv_path.exists() and not streamlit_venv_path.exists():
        print(f"\nCreating virtual environment at {venv_path}...")
        subprocess.run([sys.executable, '-m', 'venv', str(venv_path)], check=True)
        venv_created = venv_path
    else:
        # Use existing venv
        if venv_path.exists():
            venv_created = venv_path
            print(f"\nUsing existing virtual environment at {venv_path}")
        else:
            venv_created = streamlit_venv_path
            print(f"\nUsing existing virtual environment at {streamlit_venv_path}")
    
    # Determine pip path based on OS
    if os.name == 'nt':  # Windows
        pip_path = venv_created / 'Scripts' / 'pip'
        python_path = venv_created / 'Scripts' / 'python'
    else:  # Unix/MacOS
        pip_path = venv_created / 'bin' / 'pip'
        python_path = venv_created / 'bin' / 'python'
    
    # Upgrade pip
    print("\nUpgrading pip...")
    subprocess.run([str(python_path), '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)
    
    # Install requirements
    requirements_path = project_root / 'requirements.txt'
    if requirements_path.exists():
        print(f"\nInstalling dependencies from {requirements_path}...")
        subprocess.run([str(pip_path), 'install', '-r', str(requirements_path)], check=True)
    else:
        print(f"\nWarning: {requirements_path} not found!")
    
    # Create activation helper script
    if os.name == 'nt':  # Windows
        activate_cmd = f"cd /d {project_root} && {venv_created}\\Scripts\\activate"
        helper_ext = 'bat'
    else:  # Unix/MacOS
        activate_cmd = f"cd {project_root} && source {venv_created}/bin/activate"
        helper_ext = 'sh'
    
    helper_path = project_root / f'activate.{helper_ext}'
    with open(helper_path, 'w') as f:
        if os.name == 'nt':
            f.write(f"@echo off\n{activate_cmd}\n")
        else:
            f.write(f"#!/bin/bash\n{activate_cmd}\n")
    
    if os.name != 'nt':
        os.chmod(helper_path, 0o755)
    
    print(f"\n✅ Setup complete!")
    print(f"\nTo activate the virtual environment:")
    print(f"  - Run: {activate_cmd}")
    print(f"  - Or use the helper: ./{helper_path.name}")
    print(f"\nTo run the app:")
    print(f"  1. Activate the virtual environment")
    print(f"  2. Run: streamlit run streamlit_app/app_hardcoded_v1.py --server.port 8502")
    
    return venv_created

def main():
    try:
        setup_venv()
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error during setup: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()