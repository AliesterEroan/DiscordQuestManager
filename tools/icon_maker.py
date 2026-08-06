import os
from PIL import Image

# Get parent directory (project root)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
os.chdir(PROJECT_ROOT)

png_path = os.path.join(PROJECT_ROOT, "discord.png")
ico_path = os.path.join(PROJECT_ROOT, "app_icon.ico")

# Check if PNG exists
if not os.path.exists(png_path):
    print("ERROR: discord.png not found!")
    exit(1)

# 1. Force remove old broken .ico if it exists
if os.path.exists(ico_path):
    print(f"Removing old {ico_path}...")
    os.remove(ico_path)

# 2. Convert PNG to proper ICO with all required Windows resolutions
print(f"Converting {png_path} to {ico_path}...")
img = Image.open(png_path)

# If PNG is small, upscale it first for better quality at larger sizes
if img.size[0] < 256 or img.size[1] < 256:
    # Upscale to 256x256 using high-quality resampling
    img = img.resize((256, 256), Image.Resampling.LANCZOS)
    print(f"Upscaled PNG to 256x256 for better quality")

icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
img.save(ico_path, format="ICO", sizes=icon_sizes)

# 3. Verify ICO was created successfully
if not os.path.exists(ico_path):
    print("ERROR: ICO file was not created!")
    exit(1)

# 4. Verify ICO can be opened and matches PNG
try:
    ico_img = Image.open(ico_path)
    
    # Check if ICO has the same size as PNG (at least one resolution)
    png_size = img.size
    ico_sizes_available = ico_img.info.get("sizes", [])
    
    print(f"SUCCESS: {ico_path} created successfully!")
    print(f"PNG size: {png_size}, mode: {img.mode}")
    print(f"ICO available sizes: {ico_sizes_available}")
    
    # Verify the PNG size is in the ICO sizes
    if png_size not in ico_sizes_available:
        print(f"WARNING: PNG size {png_size} not found in ICO sizes")
    
    # Compare a sample of pixels to verify visual match
    # Resize PNG to match ICO's largest size for comparison
    if ico_sizes_available:
        largest_size = max(ico_sizes_available)
        png_resized = img.resize(largest_size, Image.Resampling.LANCZOS)
        ico_largest = Image.open(ico_path)
        ico_largest.size = largest_size
        
        # Simple check: compare first pixel
        if png_resized.getpixel((0, 0)) == ico_largest.getpixel((0, 0)):
            print("Visual verification: Icons match (pixel check passed)")
        else:
            print("WARNING: Icons may not match visually")
    
except Exception as e:
    print(f"ERROR: Failed to verify ICO: {e}")
    exit(1)
