#!/usr/bin/python2.1
# Ircbot for local urls.

import ircbot, urlbot2

server=("localhost",6667)
nick="urlbot"
channels=["#jauterourls"]

bot=ircbot.Bot(nick=nick,channels=channels)
bot.restart=0

def invite(m, origin, args, text, bot=bot):
    chan=text
    if chan in bot.channels:
        bot.todo(['JOIN', chan])

def leave(m, origin, args, text, bot=bot):
    if text=="restart":
        bot.restart=1
    bot.todo(['QUIT'], "bye bye!")

bot.rule(invite,'invite',cmd="INVITE")
bot.rule(leave,'leave',cmd="KICK")

urlbot2.init_bot(bot)
ircbot.doubleFork()

bot.run(server[0],server[1])

urlbot2.uninit_bot(bot)
