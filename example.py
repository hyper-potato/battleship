# The player class is contained in player.py. This is the class you will
# update with your game logic
from player import Player

# The BattleshipGame class is the main game engine. You don't need to dos
# anything with it, but you can use it to test your Player implementations.
from battleship_game import BattleshipGame

# To construct a player, call the constructor with a name
# For our tournament, this name will be your team name
p1 = Player('Dreamsign')

# get_board calls the player's board generation logic. The default
# implementation returns a static board with the same layout every time.
# You should experiment with board layout logic to confuse your opponents.
my_board = p1.get_board()

# printing the board shows a graphic representation
print(my_board)

# The next_shot method returns the player's next shot at the board.
# The framework will call this automatically, but you can test it here
# to see how it works. The defalut implementation fires randomly every time
# next_shot is called.
print(p1.next_shot())


# Let's create a second player/team
p2 = Player('Rabidfall')

# Create a new game, pitting the 2 players against each other.
g = BattleshipGame(-1, p1, p2)

# The run method runs the game until someone wins. p1 always shoots first.
# In each tournament, you will play each opponent 10 - 1000 times alternating
# which player goes first.
#
# You'll notice that a game between two naive players takes many hundreds of
# turns! It shouldn't take this long - you should be able to do better.
log = g.run()

for line in log:
    print(line)
