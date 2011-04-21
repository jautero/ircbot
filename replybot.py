import random
replies=["A likely story","I don't see what that has to do with anything",
         "Was that a calculated insult, or merely simple habitual rudeness?"]

def init_bot(bot):
    def send_reply(m, origin, args, text, bot=bot):
        """Send random reply when bot's nick is mentioned"""
        if not bot.replied:
            reply=random.choice(replies)
            bot.safeMsg(origin.sender, [reply])
        else:
            bot.replied=0

    bot.rule(send_reply,'reply',bot.nick)
    bot.replied=0

def uninit_bot(bot):
    pass
