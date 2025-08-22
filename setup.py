#!/usr/bin/env python3
"""
BNS Legal Assistant - Automated Setup Script
Cross-platform setup for Windows, Mac, and Linux
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

class BNSSetup:
    def __init__(self):
        self.platform = platform.system().lower()
        self.python_cmd = self.get_python_command()
        self.pip_cmd = f"{self.python_cmd} -m pip"
        
    def get_python_command(self):
        """Get the appropriate Python command for this system."""
        python_commands = ['python3', 'python']
        
        for cmd in python_commands:
            try:
                result = subprocess.run([cmd, '--version'], 
                                      capture_output=True, text=True, check=True)
                if 'Python 3.' in result.stdout:
                    return cmd
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        raise RuntimeError("Python 3.7+ is required but not found. Please install Python 3.7 or higher.")
    
    def print_header(self):
        """Print setup header."""
        print("=" * 60)
        print("🏛️  BNS Legal Assistant Setup")
        print("   AI-Powered Legal Consultation System")
        print("=" * 60)
        print(f"Platform: {platform.system()} {platform.release()}")
        print(f"Python: {self.python_cmd}")
        print()
    
    def check_python_version(self):
        """Check if Python version is compatible."""
        print("📋 Checking Python version...")
        
        try:
            result = subprocess.run([self.python_cmd, '--version'], 
                                  capture_output=True, text=True, check=True)
            version_str = result.stdout.strip()
            print(f"   ✅ Found {version_str}")
            
            # Extract version numbers
            version_parts = version_str.split()[1].split('.')
            major, minor = int(version_parts[0]), int(version_parts[1])
            
            if major < 3 or (major == 3 and minor < 7):
                raise RuntimeError(f"Python 3.7+ required, found {version_str}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
        
        return True
    
    def create_virtual_environment(self):
        """Create virtual environment."""
        print("🔧 Creating virtual environment...")
        
        venv_path = Path("venv")
        if venv_path.exists():
            print("   ⚠️  Virtual environment already exists")
            return True
        
        try:
            subprocess.run([self.python_cmd, '-m', 'venv', 'venv'], check=True)
            print("   ✅ Virtual environment created")
            return True
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to create virtual environment: {e}")
            return False
    
    def activate_virtual_environment(self):
        """Get activation command for virtual environment."""
        if self.platform == 'windows':
            return 'venv\\Scripts\\activate'
        else:
            return 'source venv/bin/activate'
    
    def install_dependencies(self):
        """Install Python dependencies."""
        print("📦 Installing dependencies...")
        
        # Get pip command for virtual environment
        if self.platform == 'windows':
            pip_cmd = 'venv\\Scripts\\python -m pip'
        else:
            pip_cmd = './venv/bin/python -m pip'
        
        try:
            # Upgrade pip first
            print("   📊 Upgrading pip...")
            subprocess.run(pip_cmd.split() + ['install', '--upgrade', 'pip'], check=True)
            
            # Install requirements
            print("   📚 Installing requirements...")
            subprocess.run(pip_cmd.split() + ['install', '-r', 'requirements.txt'], check=True)
            
            print("   ✅ Dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to install dependencies: {e}")
            return False
    
    def create_directories(self):
        """Create necessary directories."""
        print("📁 Creating directories...")
        
        directories = ['data', 'data/vector_db', 'logs']
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print(f"   ✅ Created {directory}")
        
        return True
    
    def setup_environment_file(self):
        """Set up environment configuration."""
        print("⚙️  Setting up environment configuration...")
        
        env_file = Path('.env')
        example_file = Path('.env.example')
        
        if env_file.exists():
            print("   ⚠️  .env file already exists")
            return True
        
        if example_file.exists():
            shutil.copy(example_file, env_file)
            print("   ✅ Created .env from template")
            print("   ⚠️  Please edit .env file and add your OpenAI API key")
        else:
            print("   ❌ .env.example template not found")
            return False
        
        return True
    
    def create_run_scripts(self):
        """Create platform-specific run scripts."""
        print("🚀 Creating run scripts...")
        
        if self.platform == 'windows':
            # Create Windows batch file
            batch_content = """@echo off
echo Starting BNS Legal Assistant...
echo.

REM Activate virtual environment
call venv\\Scripts\\activate

REM Check if .env file exists
if not exist .env (
    echo Error: .env file not found!
    echo Please copy .env.example to .env and configure your settings.
    pause
    exit /b 1
)

REM Start the application
python app.py

pause
"""
            with open('run.bat', 'w') as f:
                f.write(batch_content)
            print("   ✅ Created run.bat for Windows")
        
        # Create shell script for Unix-like systems
        shell_content = """#!/bin/bash
echo "Starting BNS Legal Assistant..."
echo

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please copy .env.example to .env and configure your settings."
    exit 1
fi

# Start the application
python app.py
"""
        with open('run.sh', 'w') as f:
            f.write(shell_content)
        
        # Make shell script executable
        if self.platform != 'windows':
            os.chmod('run.sh', 0o755)
            print("   ✅ Created run.sh for Unix-like systems")
        
        return True
    
    def print_completion_message(self):
        """Print setup completion message."""
        print()
        print("=" * 60)
        print("🎉 Setup Complete!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Edit the .env file and add your OpenAI API key")
        print("2. Place BNS PDF documents in the 'data' directory")
        print("3. Run the application:")
        
        if self.platform == 'windows':
            print("   • Windows: Double-click run.bat or run 'run.bat' in command prompt")
        print("   • Unix/Linux/Mac: Run './run.sh' in terminal")
        print("   • Manual: Activate venv and run 'python app.py'")
        print()
        print("4. Open your browser to http://localhost:5000")
        print()
        print("📖 For detailed documentation, see the docs/ directory")
        print("🐛 For troubleshooting, see docs/TROUBLESHOOTING.md")
        print()
        
        # Environment-specific notes
        print("Important notes:")
        print("• OpenAI API key is required - get one from https://platform.openai.com/")
        print("• Place BNS PDF files in the 'data' directory before first run")
        print("• The system will automatically process PDFs on first startup")
        print("• Check logs in bns_legal_assistant.log for debugging")
        print()
    
    def run_setup(self):
        """Run the complete setup process."""
        self.print_header()
        
        steps = [
            ("Check Python version", self.check_python_version),
            ("Create virtual environment", self.create_virtual_environment),
            ("Install dependencies", self.install_dependencies),
            ("Create directories", self.create_directories),
            ("Setup environment file", self.setup_environment_file),
            ("Create run scripts", self.create_run_scripts)
        ]
        
        for step_name, step_function in steps:
            if not step_function():
                print(f"❌ Setup failed at: {step_name}")
                return False
            print()
        
        self.print_completion_message()
        return True

def main():
    """Main setup function."""
    try:
        setup = BNSSetup()
        success = setup.run_setup()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️  Setup interrupted by user")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()