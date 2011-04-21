#!/usr/bin/python

class match:
    stone="kivi"
    paper="paperi"
    scissors="sakset"
    draw="tasapeli"
        
    def __init__(self,players):
        self.players=players
        self.results=[None]*len(players)

    def stone(self,result):
        return result==self.stone
    def paper(self,result):
        return result==self.paper
    def scissors(self,result):
        return result==self.scissors

    def winner(self):
        if len(result)>2:
            return None
        if self.results[0]==None or self.results[1]==None:
            return None
        if self.results[0]==self.results[1]:
            return self.draw
        if ((self.stone(self.results[0]) and self.scissors(self.results[1])) or
            (self.paper(self.results[0]) and self.stone(self.results[1])) or
            (self.scissors(self.results[0]) and self.paper(self.results[1]))):
            return self.player[0]
        else:
            return self.player[1]

    def set_result(self,player,result):
        try:
            i=self.players.find(player)
            self.results[i]=result
        except:
            pass
    
matches={}

def challenge(
