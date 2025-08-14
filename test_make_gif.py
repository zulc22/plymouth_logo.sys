#!/usr/bin/python3

from PIL import Image
from sys import argv
import logo

"""
	Convert logo.sys file to gif
	Usage: test_make_gif.py <path/to/logo.sys> [--expand]
	'--expand' doubles the pixels horizontally.
"""

if __name__=="__main__":

	SOURCE_FILE = argv[1]
	EXPAND = argv[2] == "--expand"

	source_pil = Image.open(SOURCE_FILE)
	source_bmp = logo.BitmapFile(SOURCE_FILE)

	if EXPAND:
		source_pil = source_pil.resize(
			(source_pil.size[0]*2, source_pil.size[1]),
			Image.Resampling.NEAREST
		)

	animation = []
	for palette in logo.ColorTableAnimation(source_bmp):
		new_im = source_pil.copy()
		new_im.putpalette([v for rgbpair in palette for v in rgbpair])
		animation.append(new_im)

	source_pil.save("logo.gif", save_all=True, append_images=animation,
		loop=0)