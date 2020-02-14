import random
from ship import Ship
from board import Board
from position import Position


# This is a naive implementation of a Player class that:
# 1. Sets up the same board every time (i.e. a static layout)
# 2. Fires randomly, without remembering which shots were hits and misses
class Player:

    # Each player has a name. There should be no need to change or delete this!
    def __init__(self, name):
        self.__name = name
        self.enemy = 100 * [' '] # record results of shot attempt
        self.__results = []
        self.__shots_so_far = []
        self.__acquire_list = []
        self.mode = "HUNT"
        self.modelist = {"HUNT": self.hunt, "ACQUIRE": self.acquire}

    def get_name(self):
        return self.__name

    def __str__(self):
        return self.get_name()

    # get_board should return a Board object containing 5 ships:
    # 1 aircraft carrier (length = 5)
    # 1 battleship (length = 4)
    # 1 cruiser (length = 3)
    # 1 submarine (length = 3)
    # 1 destroyer (length = 2)
    # You can make your own fun names for the ships, but the number and lengths
    # of the ship will be validated by the framework. Printing the board will
    # show the first letter of each ship's name.

    # This implementation returns the first sample layout from this web page:
    # http://datagenetics.com/blog/december32011/index.html
    def get_board(self):
        ships_list = [Ship('Carrier', Position('C', 2), 5, False),
                      Ship('battleship', Position('F', 5), 4, True),
                      Ship('submarine', Position('A', 2), 3, False),
                      Ship('crusier', Position('D', 9), 3, True),
                      Ship('destroyer', Position('E', 3), 2, True)]
        return Board(ships_list)
    

    
    def next_shot(self):
        
        return self.modelist[self.mode]()
    
            
    
    def acquire(self):
        if len(self.__acquire_list) == 0:
            self.mode = 'HUNT'
            self.hunt()
        
        target = self.__acquire_list[0]        
        result = Position(self.loc_convert(target)[0],self.loc_convert(target)[1])
        self.__acquire_list.pop(0)
            
        return result
        
              
               
    
    def hunt(self):
        while True: 
            (row, col) = self.random_fire() 
            if self.convert_to_loc(row, col)  not in self.__shots_so_far:
                break   
        return Position(row, col)

     
    def random_fire(self):
        row = chr(64 + random.randint(1, 10))  # A - J
        col = random.randint(1, 10)
        return row, col
    
#    def grid_picktile():
#        "Chooses a tile from grid"
#        from random import randrange
#        target = randrange(0, 91, 10)
#        target += randrange((target // 10) % 2, 10, 2)
#        return target


        
    # result is a tuple consisting of:
    # - the shot location (a Position object)
    # - whether the shot was a hit (True) or a miss (False)
    # - whether a ship was sunk (True) or not (False)
    def post_shot_result(self, result):
        self.__results.append(result)
        
        # location is expressed as 0-99
        location = result[0].get_row_idx() * 10 + result[0].get_col_idx()
        self.__shots_so_far += [location]   # stores shot location in ineger
        
        if result[1] == True: 
            self.enemy[location] = 'X'
            
            if result[2] == False:
                self.mode = "ACQUIRE"
                mark = self.__shots_so_far[-1]
                # build acquire list
#                self.__acquire_list = [target] # First element in acquire list is target location
                for direction in self.getdirs(mark):
                    if mark + direction not in self.__shots_so_far:
                        self.__acquire_list += [mark + direction] # potential targets
            else:
                self.mode = "HUNT"        
            
        else:
            self.enemy[location] = 'O'
            if len(self.__acquire_list) > 0:
                self.mode = "ACQUIRE"
            else:
                self.mode = "HUNT"
        
    
    def getdirs(self,pos):
        "get avaliable directions from pos"
        output = []
        if pos % 10 != 9: output += [1]
        if pos % 10 != 0: output += [-1]
        if pos < 90: output += [10]
        if pos > 9: output += [-10]
        return output
      
    def loc_convert(self, location):
        row = chr(65 + location // 10)
        col = location % 10 + 1
        return row, col
        
    def convert_to_loc(self, row, col): 
       return 10 * (ord(row) - 65) + col - 1