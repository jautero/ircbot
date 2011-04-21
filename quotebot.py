import random, types, os.path

quotefile=os.path.expanduser("~/Documents/quotes")

def read_quotefile(quotefile):
    if isinstance(quotefile,types.StringType):
        try:
			quotefile=open(quotefile)
		except:
			return None
    quotes=[]
    quote=[]
    for line in quotefile.readlines():
        if line.strip()=="%" and quote:
            quotes.append("".join(quote))
            quote=[]
            continue
        quote.append(line)
    if quote:
        quotes.append("".join(quote))
    return quotes

quotes=read_quotefile(quotefile)

def init_bot(bot):
    
    def bot_quote(m, origin, args, text, bot=bot):
        if not m.group(1):
            bot.safeMsg(origin.sender,random.choice(quotes).split("\n"))
            return None
        print m.group(1)
        quoteno=int(m.group(1))
        if quoteno>=0 and quoteno<len(quotes):
            bot.safeMsg(origin.sender,quotes[quoteno].split("\n"))
        else:
            bot.safeMsg(origin.sender,["Give number between 0 and %d." %
                                       len(quotes)-1])
	if quotes:
    	bot.rule(bot_quote,'quote',r'^!quote( [0-9]*)?')

def uninit_bot(bot):
    pass
