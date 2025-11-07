
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import os

def create_assets():
    """Create placeholder assets"""
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)
    
    
    icon_path = assets_dir / "icon.ico"
    if not icon_path.exists():
       
        img = Image.new('RGB', (32, 32), color='blue')
        draw = ImageDraw.Draw(img)
        draw.rectangle([8, 8, 24, 24], fill='white')
        img.save(icon_path, format='ICO')
        print("Created icon.ico")
    
 
    logo_path = assets_dir / "logo.png"
    if not logo_path.exists():
       
        img = Image.new('RGB', (64, 64), color='navy')
        draw = ImageDraw.Draw(img)
        draw.rectangle([16, 16, 48, 48], fill='lightblue')
        draw.line([20, 20, 44, 44], fill='white', width=3)
        draw.line([44, 20, 20, 44], fill='white', width=3)
        img.save(logo_path, format='PNG')
        print("Created logo.png")
    
    print("Assets created successfully!")

if __name__ == "__main__":
    create_assets()