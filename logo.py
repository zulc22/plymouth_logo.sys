#!/usr/bin/python3

import struct
import io
import itertools
import copy

class BitmapFile:
	"""
		Bitmap file parser. Doesn't implement things that do not appear
		in LOGO.SYS files.
	"""

	def __init__(self, file_or_path, close_fd=False, read_image=False):
		"""
			Accepts a file descriptor or string, and parses the bitmap file
			into the object's memory.
		"""

		file = None
	
		if type(file_or_path) is str:
			file = open(file_or_path, "rb")
			# we want to close this file descriptor if we made it
			close_fd = True
		
		if isinstance(file_or_path, io.RawIOBase):
			file = file_or_path
		
		if file is None:
			raise TypeError(f"Unhandled type: '{type(file_or_path)}'.")

		if file.read(2) != b"BM":
			if close_fd: file.close()
			raise ValueError("Bitmap doesn't start with BM.")
		
		self._header_size, \
			self._reserved_1, \
			self._reserved_2, \
			self._image_offset, \
			self._dib_size = struct.unpack("<IHHII", file.read(4+2+2+4+4))
		
		if self._dib_size != 40:
			if close_fd: file.close()
			raise ValueError("Bitmap DIB header isn't 40 bytes long. Not parsing.")
		
		self.width, \
			self.height, \
			self.planes, \
			self.bit_depth, \
			self.compression_type, \
			self._image_size, \
			self.pixels_per_meter_h, \
			self.pixels_per_meter_v, \
			self.colors_used, \
			self.colors_important = struct.unpack("<IIHHIIIIII", file.read(36))
		
		if self.bit_depth != 8:
			if close_fd: file.close()
			raise ValueError("Bitmap isn't 256 color.")
		
		if self.compression_type != 0:
			if close_fd: file.close()
			raise ValueError("Bitmap is compressed.")
		
		self.color_table = []
		for _ in itertools.repeat(None, 256):
			b,g,r = struct.unpack("BBBx", file.read(4))
			self.color_table.append((r,g,b))
		
		# 'important colors' being 0 means that *all* colors are important
		if self.colors_important == 0: self.colors_important = 256
		
		if read_image:
			file.seek(self._image_offset)
			self.image_data = file.read(self._image_size)

		if close_fd: file.close()

class ColorTableAnimation:
	"""
		Implements the Windows 9x scrolling bar animation by rotating
		the colors marked 'unimportant' at the end of the palette.
	"""

	def __init__(self, bitmap):
		# we do not want to accidentally overwrite the color table
		# of the BitmapFile object.
		self.color_table = copy.deepcopy(bitmap.color_table)
		self.colors_important = bitmap.colors_important
		self.iterations_until_loop = 256 - bitmap.colors_important

	def __iter__(self): return self

	def __next__(self):
		if self.colors_important == 256: raise StopIteration
		
		self.iterations_until_loop -= 1
		if self.iterations_until_loop == 0: raise StopIteration
		if self.iterations_until_loop == -1: # so the iterator can be reused
			self.iterations_until_loop = 256 - self.colors_important

		unimportant_colors = self.color_table[self.colors_important:]
		unimportant_colors.append(unimportant_colors.pop(0))
		self.color_table = \
			self.color_table[:self.colors_important] + unimportant_colors
		
		return self.color_table
