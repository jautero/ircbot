import pydelicious

defaultuser="jaubot"
defaultpasswd="Othem0ae"

def none2str(s):
	if s:
		return s
	else:
		return ""

class DeliciousUrlstore:
	def __init__(self,user=defaultuser,passwd=defaultpasswd):
		self.connection=pydelicious.apiNew(user,passwd)
		
	def add_url(self,url,title,description,tags,nick,channel):
		if channel and channel!="bot":
			tags.append("ircchannel:"+channel)
		if nick:
			tags.append("ircnick:"+nick)
		self.connection.posts_add(url,none2str(title),none2str(description)," ".join(tags))
