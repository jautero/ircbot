import ircbot, asynchttpd,urllib,posixpath

class PingRequestHandler(asynchttpd.RequestHandler):
    def handle_data(self):
        ircbot.debug("Got connection. path: ", self.path)
        name=posixpath.normpath(urllib.unquote(self.path)).split("/")[1]
        title=urllib.unquote(self.QUERY["title"])
        url=self.QUERY["url"]
        pinghandler=self.server.pinghandlers
        if pinghandler and pinghandler.has_key(name):
            if pinghandler[name](self.server,title,url):
                self.send_xml_error(None)
            else:
                self.send_xml_error("Failed to handle request")
        else:
            self.send_error(404,"File not found.")

    def send_xml_error(self,msg):
        self.send_response(200)
        self.send_header("Content-type","text/xml")
        self.end_headers()
        self.wfile.write('<?xml version="1.0" encoding="iso-8859-1"?>\n<response>')
        if msg:
            self.wfile.write('<error>1</error>\n')
            self.wfile.write('<message>%s</message>' % msg,)
        else:
            self.wfile.write('<error>0</error>\n')
        self.wfile.write('</response>\n')

def bot_handle_ping(server,title,url):
    try:
        for channel in server.bot.channels:
            server.bot.msg(channel,server.bot.blogmessage,{'title':title,'url':url})
    except Exception:
        return 0
    return 1

if __name__ == "__main__":
    bot=ircbot.Bot(nick="pingbot",channels=["#test"])
    def bye(m, origin, args, text, bot=bot):
        bot.todo(['QUIT'], "bye bye!")
    bot.rule(bye, 'bye', r'bye bye bot')
    server=asynchttpd.Server('localhost',8080,PingRequestHandler)
    server.bot=bot
    server.blogmessage="New blogentry: %(title)s, %(url)s"
    server.pinghandlers={'irc':bot_handle_ping}
    bot.run("localhost",6667)

    
