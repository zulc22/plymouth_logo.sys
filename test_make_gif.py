from PIL import Image
from sys import argv
import mini_bitmap_parser

SOURCE_FILE = argv[1]

source_pil = Image.open(SOURCE_FILE)
source_bmp = mini_bitmap_parser.BitmapFile(SOURCE_FILE)

animation = []
for palette in mini_bitmap_parser.ColorTableAnimation(source_bmp):
	new_im = source_pil.copy()
	new_im.putpalette([v for rgbpair in palette for v in rgbpair])
	animation.append(new_im)

source_pil.save("logo.gif", save_all=True, append_images=animation,
	loop=0)