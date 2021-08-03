import re
import codecs
import logging
import logging.handlers
import zipfile
import sys, os, time, glob
import traceback

_RE = re.compile(r"(\d*)(\w+)")
def parse_rotate_interval(s):
	m = _RE.search(s)
	if m:
		interval, when = m.groups()
		return int(interval or 1), when
	

class TimedCompressedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
	"""
	   Extended version of TimedRotatingFileHandler that compress logs on rollover.
	   by Angel Freire <cuerty at gmail dot com>
	"""

	def _appendRecord(self, msg, levelno=20, levelname="INFO", name="atualizador", **kwargs):
		record = logging.makeLogRecord(dict(msg=msg, levelno=levelno, levelname=levelname, name=name, **kwargs))
		msg = self.format(record)
		stream = self.stream
		stream.write(msg)
		stream.write(self.terminator)
		stream.flush()
		self.flush()
		
	def doRollover(self):
		"""
		do a rollover; in this case, a date/time stamp is appended to the filename
		when the rollover happens.  However, you want the file to be named for the
		start of the interval, not the current time.  If there is a backup count,
		then we have to get a list of matching filenames, sort them and remove
		the one with the oldest suffix.

		This method is a copy of the one in TimedRotatingFileHandler. Since it uses
		
		"""
		try:
			self._appendRecord("Inicio rotate")

			self.stream.close()
			# get the time that this sequence started at and make it a TimeTuple
			t = self.rolloverAt - self.interval
			timeTuple = time.localtime(t)
			dfn = self.baseFilename + "." + time.strftime(self.suffix, timeTuple)
			if os.path.exists(dfn):
				os.remove(dfn)
			os.rename(self.baseFilename, dfn)
			if self.backupCount > 0:
				# find the oldest log file and delete it
				s = glob.glob(self.baseFilename + ".20*")
				if len(s) > self.backupCount:
					s.sort()
					os.remove(s[0])
			if self.encoding:
				self.stream = codecs.open(self.baseFilename, 'w', self.encoding)
			else:
				self.stream = open(self.baseFilename, 'w')
			self.rolloverAt = self.rolloverAt + self.interval
			if os.path.exists(dfn + ".zip"):
				os.remove(dfn + ".zip")
			file = zipfile.ZipFile(dfn + ".zip", "w")
			file.write(dfn, os.path.basename(dfn), zipfile.ZIP_DEFLATED)
			file.close()
			os.remove(dfn)

			self._appendRecord("Fim rotate")
		except Exception:
			with open("log/exc.log", "a") as f:
				traceback.print_exc(file=f)

def get_logger(name="atualizador", level=logging.INFO):

	name = name or "atualizador"

	log = logging.getLogger(name)
	log.setLevel(int(level or logging.INFO))

	if os.environ.get('logfile') or getattr(sys, 'frozen', False):
		# quando eh versao producao, seta variavel onde esta a cadeia de certificados para o requests
		# e configura logs em arquivo
		#os.environ['REQUESTS_CA_BUNDLE'] = os.path.join(os.path.dirname(sys.executable), 'cacert.pem')

		## Quando for versao de producao, configura o log para gerar arquivo com rotacao e compactacao...
		if not os.path.exists('log'):
			os.mkdir('log')

		rotate_interval, rotate_when = 1, 'MIDNIGHT'
		if os.environ.get('logrotate'):
			interval_when = parse_rotate_interval(os.environ['logrotate'])
			if interval_when:
				rotate_interval, rotate_when = interval_when

		filename = name

		handler = TimedCompressedRotatingFileHandler(filename="log/{}.log".format(filename), when=rotate_when, interval=rotate_interval, encoding='utf-8')

		formatter = logging.Formatter("%(asctime)s: %(name)s: %(levelname)s: %(message)s")
		handler.setFormatter(formatter)
		log.addHandler(handler)

	else:
		logging.basicConfig(format="%(asctime)s: %(name)s: %(levelname)s: %(message)s")

	return log
