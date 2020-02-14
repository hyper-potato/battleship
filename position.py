class Position:
    def __init__(self, row, col):
        self.__row = row
        self.__col = col

    def get_row_idx(self):
        return ord(self.__row) - 65

    def get_col_idx(self):
        return self.__col - 1

    # A valid position is anywhere from (A, 1) to (J, 10)
    def validate(self):
        valid = True

        if ord(self.__row) < ord('A') or self.__col < 1:
            valid = False
        elif ord(self.__row) > ord('J') or self.__col > 10:
            valid = False

        return valid

    def __str__(self):
        return '({0}, {1})'.format(self.__row, self.__col)
