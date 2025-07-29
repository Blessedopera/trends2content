"""
Setup script for Integrated Content Creator

Run this after installing requirements to set up Playwright browsers.
"""

import subprocess
import sys

def setup_playwright():
    """Install Playwright browsers"""
    try:
        print("Installing Playwright browsers...")
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        print("✅ Playwright browsers installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing Playwright browsers: {e}")
        return False
    return True

if __name__ == "__main__":
    print("🚀 Setting up Integrated Content Creator")
    print("="*50)
    
    if setup_playwright():
        print("\n✅ Setup complete! You can now run the application with:")
        print("python main.py")
    else:
        print("\n❌ Setup failed. Please install Playwright browsers manually:")
        print("playwright install chromium")