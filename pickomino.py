#state for each tile 

from enum import Enum

class Tile(Enum):
	FACE_UP = 1
	FACE_DOWN = 2
	OWNED = 3 #not necessarly on top of a pile

class Pickomino():
	#even player goes first
	worms_on_tile = [1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4]
	
	def __init__(self):
		self.tile = [Tile.FACE_UP]*16
		self.turn = 1
		self.player_pile = [[],[]]

		self.tile_available = 16

	def return_tile(self):
		me = self.turn%2
		#return top tile and turn max tile down if it's not the tile we just returned
		if (len(self.player_pile[me])>0):#the player has a tile
			tile_returned = self.player_pile[me].pop()
			self.tile[tile_returned]= Tile.FACE_UP
			self.tile_available += 1

			for i in range(15,-1,-1):
				if self.tile[i]==Tile.FACE_UP:
					if i==tile_returned:
						return
					self.tile[i]=Tile.FACE_DOWN
					return

	def make_move(self,i):
		#we consider that the score is either an integer>=21 or None, 

		#do you have to steal the tile when exact score ?, no you can overlook it
		self.turn += 1
		me = self.turn%2
		adv = (self.turn+1)%2

		if i==None:#round failed because no more available faces or no worm
			self.return_tile()
			return

		elif self.tile[i]==Tile.OWNED and len(self.player_pile[adv])>0 and i==self.player_pile[adv][-1]:
			#can steal the adversary's tile
			self.player_pile[adv].pop()
			self.player_pile[me].append(i)
			return

		else:
			for j in range(i,-1,-1):
				if self.tile[j]==Tile.FACE_UP:
					self.player_pile[me].append(j)
					self.tile[j]=Tile.OWNED
					self.tile_available-=1
					return
			#we can't get a tile
			self.return_tile()
			return

	def get_current_state(self):
		return (self.tile,self.player_pile[0],self.player_pile[1])


	def game_end(self):
		return self.tile_available==0

	def get_score_players(self):
		return (sum([worms_on_tile[i] for i in self.player_pile[0]]),sum([worms_on_tile[i] for i in self.player_pile[1]]))

	def get_winner(self):
		s0,s1 = self.get_score_players()
		if s1==s2:
			m0 = max(self.player_pile[0])
			m1 = max(self.player_pile[1])
			if m0>m1:
				return 0
			return 1
		else:
			if s1>s2:
				return 0
			return 1

	def show(self):
		for i in range(21,37):
			print(i,end=" ")
		for i in range(16):
			match tile[i]:
				case Tile.FACE_UP:
					print("U  ",end="")
				case Tile.FACE_DOWN:
					print("D  ",end="")
				case Tile.OWNED:
					print("O  ",end="")

"""ways of being unsucessful:
- get dice roll with only numbers you already have
- doesn't have a worm at the end of the turn
- unable to reach the score of a visible tile

the two first are determined earlier when we make the player play its turn"""