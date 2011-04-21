#!/usr/bin/python
# Ircbot for pinging.

import time

class pingstat:
    def __init__(self,nick):
        self.nick=nick
        self.requests=0
        self.responses=0
        self.min=0
        self.max=0
        self.avg=0
        self.pending=[]

    def ping(self,sender):
        timestamp=int(time.time())
        self.requests=self.requests+1
        self.pending.append((sender,timestamp))

    def pong(self,target):
        timestamp=int(time.time())
        if target:
            pinglist=[ping for ping in self.pending if ping[0]==target]
        else:
            pinglist=self.pending
        if pinglist:
            item=pinglist[-1]
            timedelta=timestamp-item[1]
            if timedelta<self.min:
                self.min=timedelta
            if timedelta>self.max:
                self.max=timedelta
            self.avg=(self.responses*self.avg+timedelta)/(self.responses+1)
            self.responses=self.responses+1
            if target:
                self.pending=[ping for ping in self.pending if ping[0]!=target]
            else:
                self.pending=[]

    def getstat(self):
        if self.responses > 0:
            loss= 100 - (self.responses*100/self.requests)
        else:
            loss= 100
        return {'nick':self.nick, 'requests': self.requests,
                'responses': self.responses, 'loss': loss,
                'min': self.min, 'max': self.max, 'avg': self.avg}

class pingstats:
    def __init__(self):
        self.statmap={}

    def ping(self,sender,target):
        if self.statmap.has_key(target):
            item=self.statmap[target]
        else:
            item=pingstat(target)
            self.statmap[target]=item
        item.ping(sender)

    def pong(self,sender,target):
        if self.statmap.has_key(sender):
            self.statmap[sender].pong(target)

    def stats(self,nick):
        if self.statmap.has_key(nick):
            return """--- %(nick)s ping statistics ---
%(requests)d packets transmitted, %(responses)d packets received, %(loss)d%% packet loss
round-trip min/avg/max = %(min)d/%(avg)d/%(max)d s""" % self.statmap[nick].getstat()
        else:
            return """ping: Unknown nick %s """ % nick


def init_bot(bot):
    def ping(m, origin, args, text, bot=bot):
        """Ping a nick with "ping: <nick>". See also pong and stats."""
        target=m.group(1)
        source=origin.nick
        if target==bot.nick:
            bot.msg(origin.sender,"%s: pong" % source)
        bot.pingstats.ping(source,target)

    def pong(m, origin, args, text,bot=bot):
        """Respond ping with "<nick>: pong" or "pong". See also ping and stats."""
        target=m.group(2)
        source=origin.nick
        bot.pingstats.pong(source,target)

    def stats(m, origin, args, text, bot=bot):
        """Get stats for nick with "stats <nick>". See also ping and pong."""
        bot.safeMsg(origin.sender, bot.pingstats.stats(m.group(1)).split("\n"))

    bot.pingstats=pingstats()    
    bot.rule(ping,'ping','^(.*): ping$')
    bot.rule(pong,'pong','^((.*): )?pong$')
    bot.rule(stats,'stats','^stats (.*)$')
           
def uninit_bot(bot):
    pass
