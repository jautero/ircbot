
class evalbot:
    def __init__(self,bot):
        self.bot=bot
        self.values={}
        self.nicks=[]

    def handle_eval(self, m, origin, args, text, bot=None):
        if not bot:
            bot=self.bot
        target=args[1]
        if target==bot.nick:
            target=origin.nick
            if not target in self.nicks:
                return
        else:
            if not origin.nick in self.nicks:
                self.nicks.append(origin.nick)
        evalstring=m.group(1)
        result=str(eval(evalstring))
        self.bot.safeMsg(target,[result])

    def get(self,name):
        return self.values.get(name,None)

    def set(self,name,value):
        self.values[name]=value
            
def init_bot(bot):
    evaluator=evalbot(bot)
    bot.rule(evaluator.handle_eval, "eval", r'^!eval (.*)$')
    bot.evaluator=evaluator

def uninit_bot(bot):
    bot.evaluator=None

