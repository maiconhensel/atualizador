import os
import sys
import string
from hashlib import md5
import random
import binascii
from io import BytesIO

from Crypto.Cipher import AES, DES

def strsum(s):
	t = 0
	for l in s:
		i = (string.digits+string.ascii_lowercase).find(l)
		t += i

	return t % 24


def md5sum(fname):
	h = md5()
	with open(fname, 'rb') as f:
		for chunk in iter(lambda: f.read(4096), b''):
			h.update(chunk)
	return h.hexdigest()


class LxCrypto:
	def __init__(self):
		self.magic = b'ctx\001'
		self.module = AES

	def get_sys_key(self, o=None):
		'''Pega a chave do sistema atual'''

		if o:
			serial = o
		elif sys.platform == "win32":
			import win32api
			serial = win32api.GetVolumeInformation("C:\\")[1]
		else:
			serial = os.stat("/usr/local")[1]

		s = md5()
		s.update(bytes(str(serial), 'ascii'))
		hardkey = s.hexdigest()

		syskey = ''
		i = 0

		while hardkey:
			if i % 4 == 0 and i: syskey += "-"
			s = strsum("%d" % int(hardkey[:2], 16))
			syskey += chr(s+65)
			hardkey = hardkey[2:]
			i += 1

		return syskey

	def decrypt_key(self, content):
		k = self.get_sys_key().encode('utf8') + b"\x01\x0a\xff\x06\x14\x8e\x84"
		lines = [line for line in content.split('\n') if line.strip() and not line.startswith('#')]
		cipher = AESCipher(k)
		lines = "\n".join(lines)
		return cipher.decrypt(lines).decode('latin1')

	def encrypt(self, key, content):
		cipher = AESCipher(key)
		return cipher.encrypt(content)

	def decrypt(self, key, content):
		cipher = AESCipher(key)
		return cipher.decrypt(content)

	def GenerateIV(self, length):
		IV= b''
		for i in range(0, length):
			IV=IV + bytes([int(256*random.random())])
		return IV
		
	def encipher(self, key, s):
		"""Compatibilidade com LztCrypto"""
		secret = b''
		key = md5(key).digest()

		IV= b''
		for i in range(0, self.module.block_size):
			IV= IV + b'A'

		if True: #(self.module.key_size == 0):
			cipherobj = self.module.new(key, self.module.MODE_CBC, IV)
		else:
			cipherobj = self.module.new(key[0:self.module.key_size], self.module.MODE_CBC, IV)

		secret += (self.magic+b'AES'+b'\0')

		data = self.GenerateIV(self.module.block_size)
		data = data + self.magic + bytes(str(len(s)), 'ascii') + b'\0'
		data = data + s

		padding = self.module.block_size - (len(data) % self.module.block_size)

		for i in range(0, padding):
			data = data + bytes([i])

		ciphertext = cipherobj.encrypt(data)
		secret += ciphertext

		return secret

	def nice_encipher(self, key, s):
		"""Compatibilidade com LztCrypto"""
		return binascii.hexlify(self.encipher(key, s))

	def decipher(self, key, s):
		"""Compatibilidade com LztCrypto"""
		fi = BytesIO(s)

		if (fi.read(len(self.magic)) != self.magic):
			raise Exception('Does not seem to be a ciphered file')

		t=b''
		while (1):
			c=fi.read(1)
			if (ord(c)==0): break
			t=t+c

		key = md5(key).digest()

		IV = b''
		for i in range(0, self.module.block_size):
			IV= IV + b'A'

		data = fi.read()

		if True: #(self.module.key_size==0):
			cipherobj = self.module.new(key, self.module.MODE_CBC, IV)
		else:
			cipherobj = self.module.new(key[0:self.module.key_size], self.module.MODE_CBC, IV)

		plain = cipherobj.decrypt(data)			  # Decrypt the data
		plain = plain[self.module.block_size:]	  # Discard first block of random data

		if (plain[0:len(self.magic)] != self.magic):
			raise Exception('Incorrect key or cipher algorithm')
		else: 
			plain=plain[len(self.magic):]

		i = plain.find(b'\0')
		length = int(plain[0:i])

		return plain[i+1:i+1+length]

	def nice_decipher(self, key, s):
		"""Compatibilidade com LztCrypto"""

		return self.decipher(key, binascii.unhexlify(s))

class LxSimpleCrypto:
	'''Classe para criptografia simples de strings'''

	def __init__(self):
		self.module = DES

	def cipherobj(self, key):
		'''Retorna o objeto de criptografia para a chave'''

		key = md5(key).digest()

		if (self.module.key_size == 0):
			cipherobj = self.module.new(key, self.module.MODE_CBC)
		else:
			cipherobj = self.module.new(key[0:self.module.key_size], mode=self.module.MODE_CBC, IV=b"\0\0\0\0\0\0\0\0")

		return cipherobj

	def encipher(self, key, s):
		'''Retorna string criptografada'''

		data = bytes(str(len(s)), "ascii") + b"\0" + s

		padding = self.module.block_size - (len(data) % self.module.block_size)

		for i in range(0, padding):
			data = data + bytes(chr(i), "ascii")
		
		cipherobj = self.cipherobj(key)
		r = cipherobj.encrypt(data)

		hexlist = ["%02X" % x for x in r]
		return ''.join(hexlist)

	def decipher(self, key, s):
		'''Retorna string descriptografada'''

		r = []
		for i in range(int(len(s)/2)):
			t = s[2*i:(2*i)+2]
			r.append(int(t, 16))
		r = bytes(r)

		cipherobj = self.cipherobj(key)
		plain = cipherobj.decrypt(r)

		return plain.split(b"\0")[-2]

# Fonte: http://stackoverflow.com/questions/14389336/why-does-pycrypto-not-use-the-default-iv
# Funciona no python 2.7 e 3.4 com PyCrypto 2.4 e 2.6
# nao funciona no 2.2 pq o pycrypto nao tem o modulo Random :/ (talvez se achar atualizado...)
# padding sempre aleatorio entao o texto criptografado sempre muda, mas descriptografa normal...
import base64

from Crypto import Random

class AESCipher:

	def __init__(self, key):
		self.bs = 32
		if len(key) >= 32:
			self.key = key[:32]
		else:
			self.key = self._pad(key)

	def encrypt(self, raw):
		raw = self._pad(raw)
		iv = Random.new().read(AES.block_size)
		cipher = AES.new(self.key, AES.MODE_CBC, iv)
		return base64.b64encode(iv + cipher.encrypt(raw))

	def decrypt(self, enc):
		enc = base64.b64decode(enc)
		iv = enc[:AES.block_size]
		cipher = AES.new(self.key, AES.MODE_CBC, iv)
		return self._unpad(cipher.decrypt(enc[AES.block_size:]))

	def _pad(self, s):
		return s + (self.bs - len(s) % self.bs) * bytes([self.bs - len(s) % self.bs])

	def _unpad(self, s):
		return s[:-ord(s[len(s)-1:])]

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from base64 import standard_b64encode, b64decode

class LxCryptoRSA:
	"""
	Fornece suporte a criptografia assimétrica RSA (Rivest-Shamir-Adleman)

	Os diretórios para leitura e gravação das chaves são:
	Dev: 'devel\\certificates'
	Produção: 'certificates'
	"""
	def __init__(self, private_key_name=None, public_key_name=None, cryptography_length=2048, certificate_dir=None):
		"""
			Parametros.: private_key_name: Nome do arquivo que contem a chabe privada
						 public_key_name: Nome do arquivo que contem a chabe publica
						 cryptography_length: Tamanho da criptogravia utilizada
						 certificate_dir: Diretório onde se encontra o arquiuvo das chaves privada e pública
		"""

		self.default_cryptography_length = cryptography_length
		self.default_private_key_name = private_key_name or 'new_private_key.pem'
		self.default_public_key_name = public_key_name or 'new_public_key.pem'

		if certificate_dir:
			self.cert_dir = certificate_dir
		else:
			self.cert_dir = 'devel\\certificates'
			if getattr(sys, 'frozen', False):
				self.cert_dir = 'certificates'

	def encrypt(self, key_name, text_to_encrypt):
		"""
			Objetivo...: Encripta um texto utilizando RSA Assimetrico 2048
			Parametros.: key_name: Nome da chave a ser utilizada para encriptacao. Formato 'pem'
						text_to_encrypt: Texto a ser encriptado
			Retorno....: texto encriptado
		"""
		file_path = self.__get_key_path(key_name, validate_path=True)

		key = self.__load_key(file_path)

		cipher = PKCS1_OAEP.new(key=key)

		cipher_text = standard_b64encode(cipher.encrypt(bytes(text_to_encrypt, 'utf-8')))

		return cipher_text.decode()

	def decrypt(self, key_name, text_to_decrypt):
		"""
			Objetivo...: Decripta um texto utilizando RSA Assimetrico 2048
			Parametros.: key_name: Nome da chave a ser utilizada para decriptar
						text_to_decrypt: texto a ser decriptado
			Retorno....: texto decriptado
		"""
		file_path = self.__get_key_path(key_name, validate_path=True)

		key = self.__load_key(file_path)

		cipher = PKCS1_OAEP.new(key=key)

		# Devido a complexidade matematica envolvida não se pode descriptar todo o texto de uma unica vez
		decrypted_text = self.__decrypt_by_bytes(cipher, text_to_decrypt)

		return decrypted_text

	def generate_private_key(self, private_key_name=None):
		"""
			Objetivo...: Gera uma chave privada
			Parametros.: private_key_name: Nome da chave privada a ser gerada.
						Se não informado assume o atributo self.default_private_key_name
			Retorno....: N/A
		"""
		if not private_key_name:
			private_key_name = self.default_private_key_name

		private_key = RSA.generate(self.default_cryptography_length)
		private_pem = private_key.export_key().decode()

		file_path = self.__get_key_path(private_key_name)
		self.__write_key(file_path, private_pem)

	def generate_public_key(self, private_key_name, public_key_name=None):
		"""
			Objetivo...: Gera uma chave publica a partir de uma chave privada fornecida
			Parametros.: private_key_name: Nome da chave privada para ser utilizada na geração da chave pública
						public_key_name: Nome da chave publica a ser gerada. Se não informado assume o atributo self.default_public_key_name
			Retorno....: N/A
		"""
		file_path = self.__get_key_path(private_key_name, validate_path=True)

		private_key = self.__load_key(file_path)

		public_key = private_key.publickey()
		public_pem = public_key.export_key().decode()

		if not public_key_name:
			public_key_name = self.default_public_key_name
		public_key_path = self.__get_key_path(public_key_name)
		self.__write_key(public_key_path, public_pem)

	def validate_encrypt_decrypt(self, private_key_name, public_key_name, text_to_validate=None):
		""" Valida se é possível criptografar e descriptografar um texto com as chaves informadas """
		if not text_to_validate:
			text_to_validate = 'Testando encrypt e decrypt usando RSA'

		encrypted_text = self.encrypt(public_key_name, text_to_validate)
		decrypted_text = self.decrypt(private_key_name, encrypted_text)

		print('-=' * 25)
		print(f"Texto original: {text_to_validate}\n")
		print(f"Texto encriptado: {encrypted_text}\n")
		print(f"Texto descriptado: {decrypted_text}\n")

		assert decrypted_text == text_to_validate
		print('Chaves validadas com sucesso.')

	def __get_key_path(self, key_name, validate_path=False):
		key_name = key_name.lower()
		if not key_name.endswith('.pem'):
			key_name += '.pem'

		file_path = os.path.abspath(self.cert_dir)

		file_path = os.path.join(file_path, key_name)

		if validate_path and not os.path.exists(file_path):
			raise Exception(f"Arquivo de certificado não encontrado em {str(file_path)}")

		return file_path

	def __load_key(self, key_path):
		with open(key_path, 'r') as key_file:
			key = RSA.import_key(key_file.read())

		return key

	def __write_key(self, key_path, data):
		with open(key_path, 'w') as key_file:
			key_file.write(data)
			print(f"Chave gravada com sucesso em {key_path}")

	def __decrypt_by_bytes(self, cipher, text_to_decrypt):
		"""
			Objetivo...: Decripta um texto por partes e retorna o texto completo decriptado
			Parametros.: cipher: Crifra para decriptacao
						text_to_decrypt: Texto para ser decriptado
			Retorno....: texto decriptado
		"""
		default_length = self.default_cryptography_length / 8
		encrypt_byte = b64decode(text_to_decrypt.encode())
		length = len(encrypt_byte)
		if length < default_length:
			decrypt_byte = cipher.decrypt(encrypt_byte)

		else:
			offset = 0
			res = []
			while length - offset > 0:
				if length - offset > default_length:
					res.append(cipher.decrypt(encrypt_byte[offset:offset + default_length]))

				else:
					res.append(cipher.decrypt(encrypt_byte[offset:]))

				offset += default_length
			decrypt_byte = b''.join(res)

		return decrypt_byte.decode()
