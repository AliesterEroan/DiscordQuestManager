"""Build script for creating standalone executable."""

import os
import sys
import subprocess


# Change to script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def generate_icon():
    """Generate multi-resolution icon from PNG."""
    try:
        from PIL import Image
        img = Image.open('discord.png')
        img.save('discord.ico', format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
        print("Icon generated successfully.")
    except ImportError:
        print("PIL not installed. Run: pip install pillow")
        return False
    except Exception as e:
        print(f"Error generating icon: {e}")
        return False
    return True


def build_exe():
    """Build the standalone executable using PyInstaller."""
    if not os.path.exists('discord.ico'):
        print("Icon file not found. Generating...")
        if not generate_icon():
            return False

    cmd = [
        'python', '-m', 'PyInstaller',
        '--onefile',
        '--noconsole',
        '--icon=discord.ico',
        '--add-data', 'discord.png;.',
        '--name=DiscordQuestManager',
        'main.py'
    ]

    print("Building executable...")
    try:
        subprocess.run(cmd, check=True)
        print("\nBuild complete! Executable is in the 'dist' folder.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    print("Discord Quest Manager - Build Script")
    print("=" * 40)
    
    # Check dependencies
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not installed. Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
    
    build_exe()
