import os
import struct
import io

class BitmapFile:
	"""
		Bitmap file parser. Doesn't implement things that do not appear
		in LOGO.SYS files.
	"""

	def __init__(self, file_or_path, close_fd=False):
		"""
			Accepts a file descriptor or string.
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
		
		self.bm_size, \
			self.reserved_1, \
			self.reserved_2, \
			self.image_offset, \
			self.dib_size = struct.unpack("<IHHII", file.read(4+2+2+4+4))
		
		if self.dib_size != 40:
			if close_fd: file.close()
			raise ValueError("Bitmap DIB header isn't 40 bytes long. Not parsing.")
		
		self.width, \
			self.height, \
			self.planes, \
			self.bit_depth, \
			self.compression_type, \
			self.image_size, \
			self.pixels_per_meter_h, \
			self.pixels_per_meter_v, \
			self.colors_used, \
			self.colors_important = struct.unpack("<IIHHIIIIII", file.read(36))
		
		if self.bit_depth != 8:
			if close_fd: file.close()
			raise ValueError("Bitmap isn't 256 color.")