class State():
    dices : tuple
    score : int
    used : set
    def __init__(self, dices, score, used) -> None:
        self.dices = dices
        self.score = score 
        self.used = used
        self._hash = None

    def __hash__(self) -> int:
        if self._hash is None:
            self._hash = hash((self.dices, tuple(self.used), self.score))
        return self._hash

    def __eq__(self, other):
        if isinstance(other, State):
            return hash(self) == hash(other)
        return False

    def __repr__(self):
        return f"{self.dices} {self.score} {self.used}"
    
    def countDices(self):
        return len(self.dices)
    
    def getDices(self):
        return set(self.dices)
    
    def getUsedDices(self):
        return self.used
    
    def getDiceCount(self, dice):
        return self.dices.count(dice)
    
    def getScore(self):
        return self.score
    
    def getChoices(self):
        return set(self.dices).difference(self.used)
