#!/usr/local/bin/python2.4
# Ircbot for pinging.

import ircbot, time, urlbot3, pingbot, os, sys, reminderbot, replybot
# quotebot, evalbot, pinky, delistore

debuglog=open("debug.log","w")

def debug(*args):
    debuglog.write("%s: "% (time.asctime()))
    for a in args: 
        debuglog.write(str(a))
    debuglog.write("\n")
    debuglog.flush()

ircbot.debug=debug

server=("irc.kolumbus.fi",6667)
nick="schemebot"
name="Bot by Juha Autero <jautero@iki.fi>"
channels=["#espoohacklab"]

bot=ircbot.Bot(nick=nick,channels=channels,name=name)
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

urlstore=urlbot3.DummyStore(False)


urlbot3.init_bot(bot,urlstore)
pingbot.init_bot(bot)
reminderbot.init_bot(bot)
#pinky.init_bot(bot)
replybot.init_bot(bot)
#quotebot.init_bot(bot)
#evalbot.init_bot(bot)

ircbot.doubleFork()

bot.run(server[0],server[1])

#evalbot.uninit_bot(bot)
#quotebot.uninit_bot(bot)
urlbot3.uninit_bot(bot)
pingbot.uninit_bot(bot)
reminderbot.uninit_bot(bot)
replybot.uninit_bot(bot)
#pinky.uninit_bot(bot)

#if bot.restart:
#    os.execlp(sys.argv[0],sys.argv)
