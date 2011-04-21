#!/usr/bin/python
# Ircbot for bloging
#

import ircbot,xmlrpclib,md5,time,botconfig

class Blog:
    def __init__(self,uri,username=None,password=None):
        self._server=xmlrpclib.Server(uri)
        self._password=password
        self._username=username

    def post(self,entry):
        """Implement in children."""

class LiveJournal(Blog):
    def post(self,entry):
        posttime=time.localtime(time.time())
        struct={}
        struct['username']=self._username
        struct['hpassword']=md5.md5(self._password).hexdigest()
        struct['event']="\n".join(entry['content'])
        struct['lineendings']='unix'
        struct['subject']=entry['subject']
        struct['year']=str(posttime[0])
        struct['mon']=str(posttime[1])
        struct['day']=str(posttime[2])
        struct['hour']=str(posttime[3])
        struct['min']=str(posttime[4])
        print self._server.postevent(struct)

class Blogger(Blog):
    blogid=""
    appkey=""
    def post(self,entry):
        self._server.blogger.newPost(self.appkey,self.blogid,
                                     self._username,self._password,
                                     "<title>%s</title>\n<category>%d</category>%s\n" % (entry['subject'],1,"\n".join(entry['content'])))

class Entry:
    def __init__(self,blog,title):
        self.text=[]
        self.addtext=0
        self.blog=blog
        self.title=title

    def add_text(self,text):
        if self.addtext:
            self.text.append(text)
        else:
            self.addtext=1

    def post(self):
        entrydict={'subject':self.title,'content':self.text}
        self.blog.post(entrydict)


bot=ircbot.Bot(nick=botconfig.botnick,channels=botconfig.botchannels)
bot.openentries={}

def blogaa(m, origin, args, text, bot=bot):
    blogname=m.group(1)
    blogtitle=m.group(2)
    print "blogaa blogiin %s otsikolla %s" % (blogname,blogtitle)
    if botconfig.blogs.has_key(blogname):
        bot.openentries[origin.nick]= Entry(botconfig.blogs[blogname],blogtitle)
        print bot.openentries
        
def postaa(m, origin, args, text, bot=bot):
    print "Postaa"
    if bot.openentries.has_key(origin.nick):
        print "postataan"
        bot.openentries[origin.nick].post()
        del bot.openentries[origin.nick]

def kokoa(m, origin, args, text, bot=bot):
    print "kokoa"
    if bot.openentries.has_key(origin.nick):
        bot.openentries[origin.nick].add_text(text)
    
def bye(m, origin, args, text, bot=bot):
    bot.todo(['QUIT'], "bye bye!")

bot.rule(bye, 'bye', r'bye bye bot')
bot.rule(blogaa, 'blogaa', r'blogaa ([^ ]*) (.*)$')
bot.rule(postaa, 'postaa', r'postaa')
bot.rule(kokoa, 'kokoa')

apply(bot.run,botconfig.ircserver)
