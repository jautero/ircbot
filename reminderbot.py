import ircbot, time

class reminderbot:
    def __init__(self,bot):
        self.bot=bot
        self.absentnicks=[]
        self.reminders={}

    def handle_remind(self, m, origin, args, text, bot=None):
        if not bot:
            bot=self.bot
        target=m.group(1)
        reminder=m.group(2)
        source=origin.nick
        if target in self.absentnicks:            
            remindstring="%s said at %s: %s" % (source,
                                                time.strftime("%H:%M"),
                                                reminder)
            if self.reminders.has_key(target):
                self.reminders[target].append(remindstring)
            else:
                self.reminders[target]=[remindstring]
            bot.safeMsg(source,["%s is not on channel. I will relay your message." % target])
    def handle_join(self, m, origin, args, text, bot=None):
        if not bot:
            bot=self.bot
        nick=origin.nick
        if self.reminders.has_key(nick) and self.reminders[nick]:
            bot.safeMsg(nick,self.reminders[nick])
            self.reminders[nick]=[]
        if nick in self.absentnicks:
            del self.absentnicks[self.absentnicks.index(nick)]

    def handle_leave(self, m, origin, args, text, bot=None):
        if not bot:
            bot=self.bot
        nick=origin.nick
        if not nick in self.absentnicks:
            self.absentnicks.append(nick)
            
def init_bot(bot):
    reminder=reminderbot(bot)
    bot.rule(reminder.handle_remind, "remind", r'^([^ :,]*)[:,] ?(.*)$')
    bot.rule(reminder.handle_join, "join", cmd="JOIN")
    bot.rule(reminder.handle_leave, "leave", cmd="PART")
    bot.reminder=reminder

def uninit_bot(bot):
    bot.reminder=None

