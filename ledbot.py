ledbottarget="ledbot"
ledbotcommand="!led"

def init_bot(bot):
    def bot_handle_url(m, origin, args, text, bot=bot):
        url=m.group(1)
        bot.safeMsg(ledbottarget," ".join(ledbotcommand,url)
    bot.rule(bot_handle_url, 'url', r'(http://[^ ]*)')
    server=asynchttpd.Server('',8080,UrlRequestHandler)

    
