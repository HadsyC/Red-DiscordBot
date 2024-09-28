from pathlib import Path
import subprocess
import sys
import os
import venv

# Paths for virtual environment and python executable
VENV_PATH = Path('.venv')
VENV_PYTHON_PATH = Path(VENV_PATH, 'bin', 'python') if not sys.platform.startswith('win') else Path(VENV_PATH, 'Scripts', 'python.exe')
REQUIREMENTS_PATH = Path('requirements/base.txt')

def create_venv():
    """Create a virtual environment if it doesn't exist."""
    if not VENV_PYTHON_PATH.exists():
        print("Creating virtual environment...")
        venv.create(VENV_PATH, with_pip=True)

def update_system_pip():
    """Update system pip to the latest version."""
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip', '--quiet'])

def update_venv_pip():
    """Update pip in the virtual environment."""
    subprocess.check_call([str(VENV_PYTHON_PATH), '-m', 'pip', 'install', '--upgrade', 'pip', '--quiet'])

def install_dependencies():
    """Install pip, wheel, and Red-DiscordBot in the virtual environment."""
    try:
        print("Upgrading pip and wheel...")
        subprocess.check_call([str(VENV_PYTHON_PATH), '-m', 'pip', 'install', '--upgrade', 'pip', 'wheel', '--quiet'])
        
        print("Installing Red-DiscordBot...")
        subprocess.check_call([str(VENV_PYTHON_PATH), '-m', 'pip', 'install', 'Red-DiscordBot', '--quiet'])

        print("Installing dependencies...")
        subprocess.check_call([str(VENV_PYTHON_PATH), '-m', 'pip', 'install', '-r', str(REQUIREMENTS_PATH), '--quiet'])
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        raise

def run_setup():
    """Run Red-DiscordBot setup with the provided configuration."""
    print("Running Redbot setup...")
    try:
        subprocess.check_call([
            str(VENV_PYTHON_PATH), 
            'redbot/setup.py', 
            '--no-prompt', 
            '--instance-name', 'Turingmaschine', 
            '--data-path', '.data', 
            '--backend', 'json', 
            '--overwrite-existing-instance'
        ])
    except subprocess.CalledProcessError as e:
        print(f"Error running Redbot setup: {e}")
        raise

def start_bot():
    """Start the Red-DiscordBot using the specified token."""
    token = os.environ.get('DISCORD_TOKEN')
    
    if not token:
        raise EnvironmentError("DISCORD_TOKEN is not set. Please set it in your environment before running the bot.")
    
    print("Starting Redbot...")
    try:
        subprocess.check_call([str(VENV_PYTHON_PATH), '-m', 'redbot', 'Turingmaschine', '--token', token, '-p', '+'])
    except subprocess.CalledProcessError as e:
        print(f"Error starting Redbot: {e}")
        raise

def main():
    """Main function to create venv, install dependencies, and run the bot."""
    # Check if the virtual environment exists and create it if not
    if not VENV_PATH.exists():
        update_system_pip()
        create_venv()
        install_dependencies()
        run_setup()
    
    # Start the Redbot
    start_bot()

if __name__ == '__main__':
    main()