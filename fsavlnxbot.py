#!/usr/bin/python2.1
# Ircbot for pinging.

import ircbot, ledbot
debuglog=open("debug.log","w")

def debug(*args):
    debuglog.write("%s: "% (time.asctime()))
    for a in args: 
        debuglog.write(str(a))
    debuglog.write("\n")
    debuglog.flush()

ircbot.debug=debug

server=("dfintra",6667)
nick="fsavbot"
channels=["#fsavlnx"]

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
ledbot.init_bot(bot)

ircbot.doubleFork()

bot.run(server[0],server[1])

ledbot.uninit_bot(bot)
