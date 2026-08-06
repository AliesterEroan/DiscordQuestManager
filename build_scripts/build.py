"""Build script for creating standalone executable."""

import os
import sys
import subprocess

# Get parent directory (project root)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
os.chdir(PROJECT_ROOT)

# Add project root to path for imports
sys.path.insert(0, PROJECT_ROOT)


def generate_icon():
    """Generate multi-resolution icon from PNG."""
    try:
        from PIL import Image
        img = Image.open(os.path.join(PROJECT_ROOT, 'discord.png'))
        img.save(os.path.join(PROJECT_ROOT, 'app_icon.ico'), format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
        print("Icon generated successfully from discord.png")
    except ImportError:
        print("PIL not installed. Run: pip install pillow")
        return False
    except Exception as e:
        print(f"Error generating icon: {e}")
        return False
    return True


def build_exe():
    """Build the standalone executable using PyInstaller."""
    # Only regenerate icon if ICO doesn't exist
    ico_path = os.path.join(PROJECT_ROOT, 'app_icon.ico')
    if not os.path.exists(ico_path):
        print("Icon file not found. Generating from PNG...")
        if not generate_icon():
            return False
    else:
        print("Using existing app_icon.ico file.")

    cmd = [
        'python', '-m', 'PyInstaller',
        '--onefile',
        '--noconsole',
        f'--icon={ico_path}',
        '--add-data', f'{os.path.join(PROJECT_ROOT, "discord.png")};.',
        '--add-data', f'{os.path.join(PROJECT_ROOT, "assets")};assets',
        '--add-data', f'{os.path.join(PROJECT_ROOT, "core", "themes", "*.json")};core/themes',
        '--add-data', f'{os.path.join(PROJECT_ROOT, "help.html")};.',
        '--name=DiscordQuestManager',
        '--distpath=' + os.path.join(PROJECT_ROOT, 'dist'),
        os.path.join(PROJECT_ROOT, 'main.py')
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
    dependencies = ['pyinstaller', 'pillow', 'pystray', 'psutil']
    for dep in dependencies:
        try:
            __import__(dep.replace('-', '_'))
        except ImportError:
            print(f"{dep} not installed. Installing...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', dep], check=True)
    
    build_exe()
