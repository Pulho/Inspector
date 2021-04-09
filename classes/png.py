import os
import binascii

class PNG:
	def __init__(self, fileName, fixFile):
	# File propriety
		self.width			= 0
		self.height			= 0
		self.colorType		= 0
		self.bitDepth		= 0
		self.data			= ""
		self.file			= fileName
		self.order			= [ ]
		self.header 		= [ ]
		self.EOF 			= [ ]
		self.chunkBytes 	= [ ]
		self.fix			= fixFile
# Return functions

	# retOrder: Returns the order of appearance of chunks
	def retOrder(self):
		return self.order
	
	# retData: Returns all information collected about the image
	def retData(self):
		return self.data

	# retDimension: Returns the image dimension in terms of Width x Length
	def retDimension(self):
		return str(self.width) + "x" + str(self.height)

# Basic Functions
	
	# convertHexAscii: Convert hex to ASCII
	def convertHexAscii(self,content):
		asc2 = bytes.fromhex(content).decode('utf-8')
		return asc2

	# convertHexInt: Convert hex to int value
	def convertHexInt(self, input):
		intValue = int('0x' + input,16)
		return intValue

	# addMetaOuputPrint: All information about the image will be stored using this function
	def addMetaOuputPrint(self, text):
		self.data += text + "\n"

# PNG Functions

	# checkHeaderTrailer: Function call to check Header and Trailer
	def checkHeaderTrailer(self):
		self.header = self.checkHeader(self.fix)
		self.EOF = self.checkTrailer(12, self.fix)

	# info: Function that coordinates function calls and png file inspection execution
	def info(self):
		self.checkHeaderTrailer()
		self.infoChunks()
		self.checkOrder()

	# infoChunks: It is intended to list, store, and handle chunks that appear throughout the file
	def infoChunks(self, begin=8): # Beginning in the 8 byte to get IHDR chunk
	    fileObject  = open(self.file, "r+b")
	    cur = begin
	    size = 0
	    chunkList = [ ]
	    notEnd = True
	    
	    try:
	    	while notEnd:
	    		# Chunk Size: 4 bytes that reports the chunk size
	    		fileObject.seek(cur, os.SEEK_SET)
	    		chunkSizeHex = fileObject.read(4)
	    		chunkSize = chunkSizeHex.hex()

	    		if not chunkSize:
	    			notEnd = False
	    			continue

	    		chunkSize = 0 if chunkSize == '00000000' else self.convertHexInt(chunkSize)
	    		chunkList.append(chunkSize)	

	    		# Chunk Name: 4 bytes that reports the chunk name 
	    		cur = cur + 4
	    		fileObject.seek(cur, os.SEEK_SET)
	    		chunkNameHex = fileObject.read(4)
	    		chunkName = chunkNameHex.hex()
	    		chunkName = self.convertHexAscii(chunkName)
		    	chunkList.append(chunkName)						

	    		# Chunk Content: chunkSize bytes that reports the chunk content
	    		cur = cur + 4
	    		fileObject.seek(cur, os.SEEK_SET)
	    		chunkContentHex = fileObject.read(chunkSize)

	    		# Chunk treatment: Treatment of specific chunks
	    		if chunkName == 'IHDR':
	    			self.width = chunkContentHex[:4].hex() # 4 bytes that represent width
	    			self.width = 0 if self.width == '00000000' else self.convertHexInt(self.width)
	    			self.height = chunkContentHex[4:8].hex() # 4 bytes that represent height
	    			self.height = 0 if self.height == '00000000' else self.convertHexInt(self.height)

	    			if self.width == 0 or self.height == 0:
		    			if self.width == 0:
		    				self.addMetaOuputPrint("IHDR ERROR: Width value is 0")
		    			if self.height == 0:
		    				self.addMetaOuputPrint("IHDR ERROR: Height value is 0")
	
	    				IHDRdimension = None
	    				# If widht or height is 0, then it tries to fix it by guessing the dimension by your CRC32 (It use brute force)
	    				if self.fix:
	    					fileObject.seek(cur + chunkSize, os.SEEK_SET)
	    					CRC = fileObject.read(4).hex()
	    					IHDRdimension = self.crc(b'\x49\x48\x44\x52', chunkContentHex[8:13], CRC)
	    					self.width = IHDRdimension[0]
	    					self.height = IHDRdimension[1]
	    					fileObject.seek(cur, os.SEEK_SET)
	    					fileObject.write(IHDRdimension[2] + IHDRdimension[3])

	    				if not IHDRdimension:
	    					self.addMetaOuputPrint("IHDR ERROR: Not capable of finding file dimension")
	    				else:
	    					self.addMetaOuputPrint(f"IHDR FIX: Dimension fixed to {self.width}x{self.height}")
	    					self.width = IHDRdimension[0]
	    					self.height = IHDRdimension[1]
	    			self.bitDepth = int(chunkContentHex[8:9].hex()) # 1 byte that represent bit depth
	    			self.addMetaOuputPrint(f"Bit depth: {self.bitDepth}")

	    			self.colorType = int(chunkContentHex[9:10].hex()) # 1 byte that represent color type

	    			# Color type and bit depth validation
	    			if self.colorType == 0:
	    				specificationColor = "(Each pixel is a grayscale sample). Bit depth allowed value 1,2,4,8,16."
	    				if not self.bitDepth in [1, 2, 4, 8, 16]:
	    					self.addMetaOuputPrint(f"BIT DEPTH or COLOR TYPE ERROR: Bit depth not allowed for the specified color type")

	    			elif self.colorType == 2:
	    				specificationColor = "(Each pixel is an R,G,B triple). Bit depth allowed value 8,16."
	    				if not self.bitDepth in [8, 16]:
	    					self.addMetaOuputPrint(f"BIT DEPTH or COLOR TYPE ERROR: Bit depth not allowed for the specified color type")

	    			elif self.colorType == 3:
	    				specificationColor = "(Each pixel is a palette index. a PLTE chunk must appear). Bit depth allowed value 1,2,4,8."
	    				if not self.bitDepth in [1, 2, 4, 8]:
	    					self.addMetaOuputPrint(f"BIT DEPTH or COLOR TYPE ERROR: Bit depth not allowed for the specified color type")

	    			elif self.colorType == 4:
	    				specificationColor = "(Each pixel is a grayscale sample, followed by an alpha sample). Bit depth allowed value 8,16."
	    				if not self.bitDepth in [8, 16]:
	    					self.addMetaOuputPrint(f"BIT DEPTHorCOLOR TYPE ERROR: Bit depth not allowed for the specified color type")

	    			elif self.colorType == 6:
	    				specificationColor = "(Each pixel is an R,G,B triple, followed by an alpha sample). Bit depth allowed value 8,16."
	    				if not self.bitDepth in [8, 16]:
	    					self.addMetaOuputPrint(f"BIT DEPTH or COLOR TYPE ERROR: Bit depth not allowed for the specified color type")

	    			self.addMetaOuputPrint(f"Color Type: {str(self.colorType)} {specificationColor}")

	    		# Text chunk. Gather printable text to show in output	
	    		elif chunkName in ['iTXt', 'zTXt', 'tEXt']:
	    			self.addMetaOuputPrint(chunkName + ':\n\t' + self.convertHexAscii(chunkContentHex.hex()))
	    		elif chunkName == 'tIME':
	    			self.addMetaOuputPrint(chunkName + ':\n\t' + str(int.from_bytes(chunkContentHex[2:3], "big")) + '/' + str(int.from_bytes(chunkContentHex[3:4], "big")) + '/' + str(int.from_bytes(chunkContentHex[:2], "big")) + ' (Month/Day/Year)\n\t' + str(int.from_bytes(chunkContentHex[4:5], "big")) + ':' + str(int.from_bytes(chunkContentHex[5:6], "big")) + ':' + str(int.from_bytes(chunkContentHex[6:7], "big")) + ' (Hour:Minute:Seconds)')

	    		calculatedCRC = hex(binascii.crc32(b''.join([chunkNameHex, chunkContentHex])))[2:]
	    		
	    		while len(calculatedCRC) < 8:
	    			calculatedCRC = "0" + calculatedCRC

				# Chunk CRC: 4 bytes that reports chunk CRC32
    			cur = cur + chunkSize
    			fileObject.seek(cur, os.SEEK_SET)
    			chunkCRCHex = fileObject.read(4)
    			chunkCRC = chunkCRCHex.hex()

    			if calculatedCRC != chunkCRC: # If does not match with the calculatedCRC, add a Warning message
    				self.addMetaOuputPrint(chunkName + ' WARNING: CRC calculation does not match with the chunk. Possible loss of data')

    			chunkList.append(chunkCRC)
    			self.chunkBytes.append(chunkList)
    			chunkList = [ ]
    			cur = cur + 4
	    except EOFError:
	    	pass
	    fileObject.close()

	# checkOrder: Check chunks sorting, in case any is outside the expected site is sent an error in the output
	def checkOrder(self): 
		chunkOrder = [self.chunkBytes[i][1] for i in range(len(self.chunkBytes))]
		self.order = chunkOrder

		if chunkOrder[0] != "IHDR":
			self.addMetaOuputPrint("IHDR ERROR: Not the first Chunk")
		elif "IHDR" not in chunkOrder:
			self.addMetaOuputPrint("IHDR ERROR: There's no IHDR Chunk")

		if chunkOrder[-1] != "IEND":
			self.addMetaOuputPrint("IEND ERROR: Not the last Chunk")
		elif "IEND" not in chunkOrder:
			self.addMetaOuputPrint("IEND ERROR: There's no IHDR Chunk")

		if "IDAT" not in chunkOrder:
			self.addMetaOuputPrint("IDAT ERROR: There's no IDAT Chunk")
		else:
			indices = [index for index, chunkIDAT in enumerate(chunkOrder) if chunkIDAT == "IDAT"]
			if not sorted(indices) == list(range(min(indices), max(indices)+1)):
				self.addMetaOuputPrint("IDAT ERROR: Multiple IDATs must be consecutive")

		if self.colorType == 3:
			if "PLTE" not in chunkOrder:
				self.addMetaOuputPrint(f"PLTE ERROR: PLTE chunk must appear (Color type = {self.colorType}), but there's none.")
			elif chunkOrder.index("PLTE") > chunkOrder.index("IDAT"):
				self.addMetaOuputPrint("PLTE ERROR: Occurring after IDAT")

			if "cHRM" in chunkOrder:
				if chunkOrder.index("cHRM") > chunkOrder.index("PLTE"):
					self.addMetaOuputPrint("cHRM ERROR: Occorring after PLTE")
				elif chunkOrder.index("cHRM") > chunkOrder.index("IDAT"):
					self.addMetaOuputPrint("cHRM ERROR: Occorring after IDAT")

			if "gAMA" in chunkOrder:
				if chunkOrder.index("gAMA") > chunkOrder.index("PLTE"):
					self.addMetaOuputPrint("gAMA ERROR: Occorring after PLTE")
				elif chunkOrder.index("gAMA") > chunkOrder.index("IDAT"):
					self.addMetaOuputPrint("gAMA ERROR: Occorring after IDAT")

			if "iCCP" in chunkOrder:
				if chunkOrder.index("iCCP") > chunkOrder.index("PLTE"):
					self.addMetaOuputPrint("iCCP ERROR: Occorring after PLTE")
				elif chunkOrder.index("iCCP") > chunkOrder.index("IDAT"):
					self.addMetaOuputPrint("iCCP ERROR: Occorring after IDAT")

			if "sBIT" in chunkOrder:
				if chunkOrder.index("sBIT") > chunkOrder.index("PLTE"):
					self.addMetaOuputPrint("sBIT ERROR: Occorring after PLTE")
				elif chunkOrder.index("sBIT") > chunkOrder.index("IDAT"):
					self.addMetaOuputPrint("sBIT ERROR: Occorring after IDAT")

			if "sRGB" in chunkOrder:
				if chunkOrder.index("sRGB") > chunkOrder.index("PLTE"):
					self.addMetaOuputPrint("sRGB ERROR: Occorring after PLTE")
				elif chunkOrder.index("sRGB") > chunkOrder.index("IDAT"):
					self.addMetaOuputPrint("sRGB ERROR: Occorring after IDAT")

			if "bKGD" in chunkOrder:
				if chunkOrder.index("bKGD") < chunkOrder.index("PLTE"):
					self.addMetaOuputPrint("bKGD ERROR: Occorring before PLTE")
				elif chunkOrder.index("bKGD") > chunkOrder.index("IDAT"):
					self.addMetaOuputPrint("bKGD ERROR: Occorring after IDAT")

			if "hIST" in chunkOrder:
				if chunkOrder.index("hIST") < chunkOrder.index("PLTE"):
					self.addMetaOuputPrint("hIST ERROR: Occorring before PLTE")
				elif chunkOrder.index("hIST") > chunkOrder.index("IDAT"):
					self.addMetaOuputPrint("hIST ERROR: Occorring after IDAT")

			if "tRNS" in chunkOrder:
				if chunkOrder.index("tRNS") < chunkOrder.index("PLTE"):
					self.addMetaOuputPrint("tRNS ERROR: Occorring before PLTE")
				elif chunkOrder.index("tRNS") > chunkOrder.index("IDAT"):
					self.addMetaOuputPrint("tRNS ERROR: Occorring after IDAT")

			if "sPLT" in chunkOrder:
				if chunkOrder.index("sPLT") > chunkOrder.index("IDAT"):
					self.addMetaOuputPrint("sPLT ERROR: Occorring after IDAT")

			if "pHYs" in chunkOrder:
				if chunkOrder.index("pHYs") > chunkOrder.index("IDAT"):
					self.addMetaOuputPrint("pHYs ERROR: Occorring after IDAT")

		# Checks if theres a 
		for i in range(len(chunkOrder)):
			if chunkOrder[i] not in ['IHDR', 'IDAT', 'PLTE','cHRM', 'iCCP', 'sPLT', 'sBIT', 'sRGB', 'tRNS', 'hIST', 'pHYs', 'bKGD', 'gAMA', 'tEXt', 'iTXt', 'zTXt', 'tIME', 'IEND']:
				self.addMetaOuputPrint(f"WARNING: Weird chunk found on PNG file, named as {self.chunkBytes[i][1]} with {self.chunkBytes[i][0]} bytes of size")

	# checkCRCbytes: Transforms into bytes
	def checkCRCbytes(self,byte):
		byte = hex(byte)[2:]
		if len(byte) % 2 != 0:
			byte = "0" + byte

		while len(byte) != 8:
			byte = "00" + byte

		byte = bytearray.fromhex(byte)
		return bytes(byte)

	# crc: Dimension correction function by brute force
	def crc(self, begin, end, CRC32):
		retList = [ ]
		print("Correcting image dimension, this may take a while. . .\n\n\n")
		for height in range(1,10000): # Range of dimension guessing attempt (Height)
			for width in range(1,10000): # Range of dimension guessing attempt (Width)
				realWidth  = self.checkCRCbytes(width)
				realHeight = self.checkCRCbytes(height)

				crc = hex(binascii.crc32(begin + realWidth + realHeight + end))[2:]

				while len(crc) < 8:
					crc = "0" + crc

				if crc == CRC32: # If the calculated crc with the width and height of the attempt corresponds, then it means that it is correct
					retList.append(width)
					retList.append(height)
					retList.append(realWidth)
					retList.append(realHeight)
					return retList
		return None

	# checkTrailer: Checks if the trailer of the file is according to a png
	def checkTrailer(self, nBytes, fixFile):
	    file = open(self.file, 'r+b')
	    nBytes = (-1)*nBytes
	    headerBytes = []
	    try:
	        file.seek(nBytes, os.SEEK_END)
	        content = file.read().hex()
	        for i in range(0,len(content),2):
	            headerBytes.append(content[i:i+2])          
	    except:
	        headerBytes = "Error Trailer"
	    if headerBytes != ['00', '00', '00', '00', '49', '45', '4e', '44', 'ae', '42', '60', '82'] and not fixFile: # If the headerBytes does not match and fixFile is not True, then add a message error
	    	self.addMetaOuputPrint(f"TRAILER ERROR: Trailer not found at the end bytes of the file. Instead:\n\t" + ' '.join(headerBytes))
	    elif fixFile and headerBytes != ['00', '00', '00', '00', '49', '45', '4e', '44', 'ae', '42', '60', '82']: # If fixFile parameter is True and the headerBytes does not match, then tries to fix it
	    	self.addMetaOuputPrint(f"FIXFILE: Trailer fixed from\n\t{' '.join(headerBytes)}\n\t\tto\n\t00 00 00 00 49 45 4e 44 ae 42 60 82\n")
	    	file.seek(nBytes, os.SEEK_END)
	    	file.write(bytearray.fromhex('0000000049454e44ae426082'))
	    return headerBytes

	# checkHeader: Checks if the header of the file is according to a png
	def checkHeader(self, fixFile):
		file  = open(self.file, "r+b")
		headerBytes = []

		content = file.read(13).hex()
		for i in range(0,len(content)-2, 2):
			hexValue = content[i:i+2]
			headerBytes.append(hexValue)

		if headerBytes != ['89','50','4e','47','0d','0a','1a', '0a', '00', '00', '00', '0d'] and not fixFile: # If the headerBytes does not match and fixFile is not True, then add a message error
			self.addMetaOuputPrint(f"HEADER ERROR: Header not found at the begin bytes of the file. Instead:\n\t" + ' '.join(headerBytes))		
		elif fixFile and headerBytes != ['89','50','4e','47','0d','0a','1a', '0a', '00', '00', '00', '0d']: # If fixFile parameter is True and the headerBytes does not match, then tries to fix it
			self.addMetaOuputPrint(f"FIXFILE: Header fixed from\n\t{' '.join(headerBytes)}\n\t\tto\n\t89 50 4e 47 0d 0a 1a 0a 00 00 00 0d\n")
			file.seek(0, os.SEEK_SET)
			file.write(bytearray.fromhex('89504e470d0a1a0a0000000d'))
		return headerBytes
