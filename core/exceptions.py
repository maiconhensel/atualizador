class WorkSpaceValidateException(Exception):
	pass

class LinxPostosKeyException(Exception):
	""" Exceções da licença """
	pass

class LinxPostosKeyExpiredException(LinxPostosKeyException):
	""" Licença expirada """
	pass

class LinxPostosKeyOutdatedException(LinxPostosKeyException):
	""" Licença desatualizada """
	pass

class LinxPostosKeyDemoException(LinxPostosKeyException):
	""" Licença de demonstração """
	pass

class LinxPostosKeyRequestException(LinxPostosKeyException):
	""" Erro de retorno da conexão do atualizador da licença """
	pass

class LinxPostosKeySaveException(LinxPostosKeyException):
	""" Erro ao salvar a licença em arquivo """
	pass

class ECFKeyException(Exception):
	""" Exceções da licença da ecf.key """
	pass

class ECFKeyNotFoundException(ECFKeyException):
	""" Exceções da licença """
	pass
	
class SyncConfiguracaoException(Exception):
	""" Exceções da sincronia """
	pass	

class SyncResetException(Exception):
	""" Exceções da sincronia """
	pass

class DatabaseVersionException(Exception):
	pass

class IntranetWebServiceException(Exception):
	""" Exceções da intranet """
	pass