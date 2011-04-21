#!/usr/bin/python
# Ircbot for pinging.

import ircbot, time, urlbot3, silencer, reminderbot, quotebot, evalbot

server=("192.168.1.42",6667)
nick="testbot"
channels=["#test"]


bot=ircbot.Bot(nick=nick,channels=channels)

def stats(m, origin, args, text, bot=bot):
    bot.safeMsg(origin.sender, bot.pingstats.stats(m.group(1)).split("\n"))

def invite(m, origin, args, text, bot=bot):
    chan=text
    if chan in bot.channels:
        bot.todo(['JOIN', chan])

def leave(m, origin, args, text, bot=bot):
    bot.todo(['QUIT'], "bye bye!")

bot.rule(invite,'invite',cmd="INVITE")
bot.rule(leave,'leave',cmd="KICK")

urlbot3.init_bot(bot)
silencer.init_bot(bot)
reminderbot.init_bot(bot)
quotebot.init_bot(bot)
evalbot.init_bot(bot)

bot.run(server[0],server[1])

evalbot.uninit_bot(bot)           
urlbot3.uninit_bot(bot)
silencer.uninit_bot(bot)
reminderbot.uninit_bot(bot)
