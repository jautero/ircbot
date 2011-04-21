class buildbot:
    def __init__(self,bot):
        self.bot=bot

def init_bot(bot):
    abuildbot=buildbot(bot)
    bot.rule(abuildbot.handle_build, "build", r'^!build (.*)$')
    bot.buildbot=abuildbot

def uninit_bot(bot):
    bot.buildbot=None

