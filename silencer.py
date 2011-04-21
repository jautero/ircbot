def init_bot(bot):
    def shutup(m, origin, args, text, bot=bot):
        bot.quiet=1
    def speak(m, origin, args, text, bot=bot):
        bot.quiet=0

    bot.rule(shutup, 'shutup', r'%s: shut ?up' % (bot.nick))
    bot.rule(speak, 'speak', r'%s: speak' % (bot.nick))
    bot.quiet=0
    
def uninit_bot(bot):
    pass
