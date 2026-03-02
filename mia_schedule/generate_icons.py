#!/usr/bin/env python3
"""Generate PNG icons from SVG."""

import os
from pathlib import Path

SIZES = [72, 96, 128, 144, 152, 192, 384, 512]
ICON_DIR = Path(__file__).parent / 'static' / 'icons'
SVG_FILE = ICON_DIR / 'icon.svg'

def generate_icons():
    """Generate PNG icons from SVG using cairosvg or Pillow."""
    try:
        import cairosvg

        for size in SIZES:
            output_file = ICON_DIR / f'icon-{size}x{size}.png'
            cairosvg.svg2png(
                url=str(SVG_FILE),
                write_to=str(output_file),
                output_width=size,
                output_height=size
            )
            print(f'✅ Generated {output_file.name}')

        print('\n✅ All icons generated successfully!')

    except ImportError:
        print('⚠️  cairosvg not installed. Install it with:')
        print('    pip install cairosvg')
        print('\nAlternatively, convert SVG to PNG manually using:')
        print('  - Online tools: https://cloudconvert.com/svg-to-png')
        print('  - Inkscape: inkscape --export-type=png --export-width=512 icon.svg')
        print('  - ImageMagick: convert -resize 512x512 icon.svg icon-512x512.png')

if __name__ == '__main__':
    generate_icons()

