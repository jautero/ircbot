import asynchttp, urlparse, htmllib, formatter, ircbot

class titleparser(htmllib.HTMLParser):
    def __init__(self,formatter,verbose=0):
        htmllib.HTMLParser.__init__(self,formatter,verbose)
        self.bodytitle=("h7",None)

    def handle_starttag(self,tag,method,attrs):
        if tag in ["h1","h2","h3","h4","h5","h6"]:
            self.save_bgn()
        else:
            method(attrs)

    def handle_endtag(self,tag,method):
        if tag in ["h1","h2","h3","h4","h5","h6"] and self.bodytitle[0]>tag:
            self.bodytitle=(tag,self.save_end())
        method()

class FetchURL(asynchttp.AsyncHTTPConnection):
    def __init__(self, url, urlhandler):
        urlelements=list(urlparse.urlparse(url.url))
        ircbot.debug(urlelements,url.url)
        if urlelements[0] != "http":
            self.do_connect=False
            return
        self.do_connect=True
        self.url=url
        self.urlhandler=urlhandler
        hosttuple=urlelements[1].split(":")
        host=hosttuple[0]
        if len(hosttuple)==2:
            port=int(hosttuple[1])
        else:
            port=80
        asynchttp.AsyncHTTPConnection.__init__(self,host,port)
        urlelements[0]=""
        urlelements[1]=""
        self._path=urlparse.urlunparse(urlelements)

    def connect(self):
        if not self.do_connect:
            return 0
        else:
            asynchttp.AsyncHTTPConnection.connect(self)
            return 1

    def handle_command(self,command):
        ircbot.debug("Handle command",command)
        self.command=command
        self.putrequest(command,self._path)
        self.endheaders()
        self.getresponse()

    def handle_connect(self):
        asynchttp.AsyncHTTPConnection.handle_connect(self)
        self.handle_command("HEAD")

    def _header_data(self):
        asynchttp.AsyncHTTPConnection._header_data(self)
        if self.command=="HEAD":
            # No body, skip
            self._body_data()

    def handle_html(self):
        parser=titleparser(formatter.NullFormatter())
        parser.feed(self.response.body)
        if parser.bodytitle[1]:
            return parser.bodytitle[1]
        else:
            return parser.title

    def handle_response(self):
        title=None
        contenttype=self.response.getheader("Content-Type").split(";")[0].strip()
        ircbot.debug("content type",contenttype)
        if contenttype=="text/html":
            if self.command=="GET":
                title=self.handle_html()
            else:
                self.handle_command("GET")
                return
        else:
            title="%s file: %s" % (contenttype,self.url.url)
        ircbot.debug("Title",title)
        self.url.title=title
        self.urlhandler.add_url(self.url)
        ircbot.debug("id",id)
        self.close()
        
class UrlObject:
    def __init__(self,url,title=None,tags=None,nick=None,channel=None,description=None):
        self.url=url
        self.title=title
        self.tags=tags
        self.description=description
        self.nick=nick
        self.channel=channel

class UrlHandler:
    def __init__(self,bot,urlstore,quiet=True):
        self.bot=bot
        self.urlstore=urlstore
        self.quiet=quiet
        
    def bot_handle_url(self, m, origin,args, text, bot=None):
        if not bot:
            bot=self.bot
        url=m.group(2)
        ircbot.debug("url: ",m.group(2))

        prefix=m.group(1).strip()
        postfix=m.group(3).strip()
        if args[1]==bot.nick:
            channel="bot"
            target=origin.nick
        else:
            channel=args[1]
            target=args[1]
        nick=origin.nick
        title=None
        description=None
        tags=[]
        if prefix:
            if prefix[-1] == ":":
                title=prefix[:-1]
                if title.find(" ")==-1:
                    title=None
            else:
                tags.extend(prefix.split())
        if postfix:
            if postfix[0]==",":
                description=postfix[1:].strip()
            else:
                tags.extend(postfix.split())
        urlobject=UrlObject(url,title=title,tags=tags,description=description,channel=channel,nick=nick)
        urlobject.target=target
        titlefetch=FetchURL(urlobject,self)
        if not titlefetch.connect():
			self.add_url(urlobject)
        
    def add_url(self,url):
        self.urlstore.add_url(url.url,title=url.title,tags=url.tags,description=url.description,nick=url.nick,channel=url.channel)
        if not self.quiet:
            if not url.title:
                title=url.url
            else:
                title=url.title             
            self.bot.safeMsg(url.target,["url %s"%(title)])

        
class DummyStore:
    def __init__(self):
        pass
    def add_url(self,url,title=None,description=None,tags=None):
        pass
        
def init_bot(bot,urlstore=None):
    if not urlstore:
        urlstore=DummyStore()
    urlhandler=UrlHandler(bot,urlstore)
    bot.rule(urlhandler.bot_handle_url, 'url', r'^(.*)(https?://[^ ]*)(.*)$')
    
def uninit_bot(bot):
    pass
