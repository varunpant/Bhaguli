import re, math	
from smtplib import	SMTP
from email.MIMEText	import MIMEText
from email.Header import Header
from email.Utils import	parseaddr, formataddr


###############################################################################
#	Helpers	####################################################################
###############################################################################

def	safe_number(value):
	try:
		n = int(value)
	except:
		n = 0		
	return	n

def	start_index(page, 	count):
	return	(page - 1) * count
	
def	total_page(count, total):
	if (count == 0 or total == 0):
		return	1	
	if (count % total) == 0 :
		return	count / total 
	result = float(count) / float(total) 
	return	math.floor(result)	 + 	1

_slugify_strip_re	 = 	re.compile(r'[^\w\s-]')
_slugify_hyphenate_re	 = 	re.compile(r'[-\s]+')
def	to_url(value):		
	import	unicodedata
	if not	isinstance(value, 	unicode):
		value = unicode(value)
	value = unicodedata.normalize('NFKD', 	value).encode('ascii', 	'ignore')
	value = unicode(_slugify_strip_re.sub('	', 	value).strip().lower())
	return	_slugify_hyphenate_re.sub('-', 	value)
	
def	IsNotNull(value):
	return value is not	None and len(value)	> 0

def	validateEmail(email):
	if	len(email)	 > 	7:
		if	re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", 	email)	 != 	None:
			return	1
	return	0	
	
def	send_email(sender, 	recipient, 	subject, 	body):
	header_charset	 = 	'ISO-8859-1'
	for	body_charset in 'US-ASCII', 'ISO-8859-1', 'UTF-8':
		try:
			body.encode(body_charset)
		except	UnicodeError:
			pass
		else:
			break
	sender_name, sender_addr = 	parseaddr(sender)
	recipient_name, recipient_addr	 = 	parseaddr(recipient)
	sender_name	 = 	str(Header(unicode(sender_name), 	header_charset))
	recipient_name	 = 	str(Header(unicode(recipient_name), header_charset))	 
	sender_addr	= sender_addr.encode('ascii')
	recipient_addr = recipient_addr.encode('ascii')
	#	Create	the	message	('plain'	stands	for	Content-Type:	text/plain)
	msg	 = 	MIMEText(body.encode(body_charset), 	'plain', 	body_charset)
	msg['From']	 = 	formataddr((sender_name, 	sender_addr))
	msg['To']	 = 	formataddr((recipient_name, 	recipient_addr))
	msg['Subject']	 = 	Header(unicode(subject), 	header_charset)
	#	Send	the	message	via	SMTP	to	localhost:25
	smtp = SMTP("localhost")
	smtp.sendmail(sender, 	recipient, 	msg.as_string())
	smtp.quit()
###############################################################################
###############################################################################
###############################################################################	
