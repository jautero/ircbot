import asynchttpd, ircbot

urllist=[]

htmlheader="""<html><head><title>URLs on #soulless</title></head>
<body>
<h1>URLs on #soulless</h1>
<ul>
"""
htmlfooter="""</ul>\n</body></html>"""

class UrlRequestHandler(asynchttpd.RequestHandler):
    def handle_data(self):
        ircbot.debug("Got connection. path: ", self.path)
        self.send_response(200)
        self.send_header("Content-type","text/html")
        self.end_headers()
        self.wfile.write(htmlheader)
        for url in urllist:
            self.wfile.write('<li><a href="%s">%s</a></li>\n' % (url,url))
        self.wfile.write(htmlfooter)


def init_bot(bot):
    def bot_handle_url(m, origin, args, text, bot=bot):
        url=m.group(1)
        urllist.append(url)
    bot.rule(bot_handle_url, 'url', r'(http://[^ ]*)')
    server=asynchttpd.Server('',8080,UrlRequestHandler)

    
