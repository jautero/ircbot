import MySQLdb, asynchttp, urlparse, htmllib, formatter, ircbot

db="webapps"
user="webapp"
passwd="webapp"

dbobject=MySQLdb.connect(db=db,user=user,passwd=passwd)

def add_url(url,nick,target,title):
    if not title:
        title=url
    cursorobject=dbobject.cursor()
    cursorobject.execute("INSERT INTO ircurls (channel, time, nick, url, title) VALUES (%s, NOW(), %s, %s, %s)",
                         (target,nick,url, title))
    id=cursorobject.insert_id()
    cursorobject.close()
    dbobject.commit()
    return id

def add_title(id,title,target):
    title=title.strip()
    cursorobject=dbobject.cursor()
    cursorobject.execute("UPDATE ircurls SET title=%s where id=%s and channel=%s",(title,id,target))
    cursorobject.close()
    dbobject.commit()

def add_description(id,desc,target):
    desc=desc.strip()
    cursorobject=dbobject.cursor()
    cursorobject.execute("SELECT description FROM ircurls WHERE id=%s and channel=%s",(id,target))
    row=cursorobject.fetchone()
    if row[0]:
        desc=row[0]+desc    
    cursorobject.execute("UPDATE ircurls SET description=%s where id=%s and channel=%s",(desc,id,target))
    cursorobject.close()
    dbobject.commit()

def get_id(url,target):
    cursorobject=dbobject.cursor()
    cursorobject.execute("SELECT id FROM ircurls WHERE url=%s and channel=%s",(url,target))
    row=cursorobject.fetchone()
    cursorobject.close()
    if row:
        return row[0]
    else:
        return None

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
    def __init__(self, url, nick, target,bot):
        urlelements=list(urlparse.urlparse(url))
        if urlelements[0] != "http":
            self.do_connect=0
            return
        self.do_connect=1
        self.url=url
        self.nick=nick
        self.target=target
        self.bot=bot
        hosttuple=urlelements[1].split(":")
        host=hosttuple[0]
        if len(hosttuple)==2:
            port=int(hosttuple[1])
        else:
            port=80
        asynchttp.AsyncHTTPConnection.__init__(self,host,port)
        urlelements[0]=urlelements[1]=""
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
        try:
            quiet=self.bot.quiet
        except:
            quiet=0
        ircbot.debug("content type",contenttype)
        if contenttype=="text/html":
            if self.command=="GET":
                title=self.handle_html()
            else:
                self.handle_command("GET")
                return
        else:
            title="%s file: %s" % (contenttype,self.url)
        ircbot.debug("Title",title)
        id=add_url(self.url,self.nick,self.target,title)
        ircbot.debug("id",id)
        if not quiet:
            if not title:
                title=self.url
            if self.target == "links":
                self.bot.safeMsg(self.nick,["url%d, %s"%(id,title)])
            else:
                self.bot.safeMsg(self.target,["url%d, %s"%(id,title)])
        self.close()
        

def init_bot(bot):
    def bot_handle_url(m, origin, args, text, bot=bot):
        if m.group(1)=="id,":
            return None
        url=m.group(2)
        nick=origin.nick
        target=args[1]
        if target==bot.nick:
            target="links"
        titlefetcher=FetchURL(url,nick,target, bot)
        if not titlefetcher.connect():
            add_url(url,nick,target,None)

    def bot_handle_desc(m, origin,args, text, bot=bot):
        id=m.group(1)
        desc=m.group(2)
        target=args[1]
        if target==bot.nick:
            target="links"
        if desc[:5]=="title":
            desc=desc[6:]
            add_title(id,desc,target)
        else:
            add_description(id,desc,target)

    def bot_handle_id(m, origin,args, text, bot=bot):
        url=m.group(1)
        target=args[1]
        if target==bot.nick:
            target="links"
        id=get_id(url,target)
        if id:
            if target=="links":
                bot.safeMsg(origin.nick,["url%d, %s"%(id,url)])
            else:
                bot.safeMsg(target,["url%d, %s"%(id,url)])
            
    bot.rule(bot_handle_url, 'url', r'^(.*)(http://[^ ]*)')
    bot.rule(bot_handle_desc, 'desc', r'^url([0-9]*),(.*)$')
    bot.rule(bot_handle_id, 'id', r'^id,(http://[^ ]*)')

    
def uninit_bot(bot):
    pass
