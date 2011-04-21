import random, types, os.path

quotefile=os.path.expanduser("~/softat/ircbot/pinky.txt")

def read_quotefile(quotefile):
    if isinstance(quotefile,types.StringType):
        quotefile=open(quotefile)
    return quotefile.readlines()

quotes=read_quotefile(quotefile)

def init_bot(bot):
    
    def bot_quote(m, origin, args, text, bot=bot):
        bot.safeMsg(origin.sender,[random.choice(quotes)%origin.nick])
        bot.replied=1
        
    bot.rule(bot_quote,'pinky',r'^%s, are you pondering what I\'m pondering?'%bot.nick)
    bot.rule(bot_quote,'pinky2',r'^Are you pondering what I\'m pondering, %s?'%bot.nick)
    bot.rule(bot_quote,'pinky3',r'^Are you thinking what I\'m thinking, %s?'%bot.nick)
    bot.rule(bot_quote,'pinky4',r'^Are you pondering what I\'m pondering?')

def uninit_bot(bot):
    pass
