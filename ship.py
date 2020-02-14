class Ship:
    def get_length(self):
        return self.__length

    def is_vertical(self):
        return self.__vertical

    def get_pos(self):
        return self.__position

    def get_name(self):
        return self.__name

    def is_sunk(self):
        return self.__sunk

    def __init__(self, name, pos, length, vertical):
        self.__name = name

        # row, col position of the ship. Should be a Position object.
        self.__position = pos

        # Integer length of the ship in grid cells
        self.__length = length

        # The cells array stores hits to the ship. Initially all False
        # (ship is healthy)
        self.__cells = [False for i in range(self.__length)]

        # True = a vertical ship, False = a horizontal ship
        self.__vertical = vertical

        self.__sunk = False

    # A valid ship is 1) located at a valid grid position, and 2) does not
    # extend off the edge of the board.
    def validate(self):
        valid = True

        if not self.__position.validate():
            valid = False
        elif self.__vertical:
            if self.__position.get_row_idx() + self.__length > 10:
                valid = False
        elif self.__position.get_col_idx() + self.__length > 10:
            valid = False

        return valid

    # Returns true if a shot on pos hits this ship, False otherwise.
    # A second shot at the same position results in a miss (that part of the
    # ship is already destroyed).
    def shoot_at(self, pos):
        hit = False
        shot_row = pos.get_row_idx()
        shot_col = pos.get_col_idx()
        ship_row = self.get_pos().get_row_idx()
        ship_col = self.get_pos().get_col_idx()

        if self.is_vertical():
            if shot_col == ship_col and \
               shot_row >= ship_row and \
               shot_row < ship_row + self.get_length() and \
               not self.__cells[shot_row - ship_row]:
                hit = True
                self.__cells[shot_row - ship_row] = True
        else:
            if shot_row == ship_row and \
               shot_col >= ship_col and \
               shot_col < ship_col + self.get_length() and \
               not self.__cells[shot_col - ship_col]:
                hit = True
                self.__cells[shot_col - ship_col] = True

        if all(self.__cells):
            self.__sunk = True

        return hit

    def __str__(self):
        return '{0} at {1} (vertical = {2})'.format(self.__name,
                                                    self.__position,
                                                    self.__vertical)
