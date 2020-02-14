from ship import Ship


class Board:
    def __add_ship(self, ship):
        added = True

        s_row = ship.get_pos().get_row_idx()
        s_col = ship.get_pos().get_col_idx()

        if ship.is_vertical():
            for r in range(s_row, s_row + ship.get_length()):
                if self.__board_list[r][s_col] is None:
                    self.__board_list[r][s_col] = ship
                    self.__ship_list.append(ship)
                else:
                    # Can't add the ship if there is already a ship here!
                    added = False
        else:
            for c in range(s_col, s_col + ship.get_length()):
                if self.__board_list[s_row][c] is None:
                    self.__board_list[s_row][c] = ship
                    self.__ship_list.append(ship)
                else:
                    # Can't add the ship if there is already a ship here!
                    added = False

        return added

    def add_ships(self, ships):
        valid = True

        # Basic validation logic. There must be 5 ships.
        if not len(ships) == 5:
            print('board does not have 5 ships')
            valid = False
        else:
            lengths_list = []

            # Each ship needs to be a valid Ship object.
            for s in ships:
                if type(s) is not Ship:
                    print('{0} is not a Ship object'.format(s))
                    valid = False
                elif not s.validate():
                    print('Ship object {0} is not valid.'.format(s))
                    valid = False
                else:
                    lengths_list.append(s.get_length())

                    if not self.__add_ship(s):
                        valid = False

            # There should be 1 ship each of lengths 2, 4, and 5.
            # There should be 2 ships of length 3.
            if lengths_list.count(2) != 1 or \
               lengths_list.count(3) != 2 or \
               lengths_list.count(4) != 1 or \
               lengths_list.count(5) != 1:
                valid = False

        if valid:
            self.__valid = True
        else:
            self.__valid = False

    def is_alive(self):
        return not all([s.is_sunk() for s in self.__ship_list])

    def shoot_at(self, pos):
        hit = None

        for s in self.__ship_list:
            if s.shoot_at(pos):
                hit = s

        return hit

    def __init__(self, ships_list):
        # Makes an empty 10x10 board
        self.__ship_list = []
        self.__board_list = [[None for row in range(10)] for col in range(10)]
        self.__valid = False
        self.add_ships(ships_list)

    def validate(self):
        return self.__valid

    # Prints a simple graphic representatation of the player's board
    def __str__(self):
        board_str = '   1 2 3 4 5 6 7 8 9 10\n'

        # ASCII 65 = 'A'
        for row in range(10):
            board_str += '{0}  '.format(chr(row + 65))
            for col in range(10):
                s = self.__board_list[row][col]
                if s is None:
                    board_str += '. '
                else:
                    board_str += '{0} '.format(s.get_name()[0])
            board_str += '\n'

        return board_str
