import random
from enum import Enum


DELTA_PAIRS: list[tuple[int, int]] = [
    (dy, dx)
    for dy in (-1, 0, 1)
    for dx in (-1, 0, 1)
    if not (dy == 0 and dx == 0)
]


class CustomNotif(Enum):
    NO_BOMB = 0
    FOUND_BOMB = 1
    INVALID_COORDINATES = 2
    VALID_COORDINATES = 3
    OUT_OF_FLAG = 4
    TILE_FLAGGED = 5
    TILE_UNFLAGGED = 6


class BoardTile:
    def __init__(self) -> None:
        self.__n_surrounding_bombs = 0
        self.__revealed = False
        self.__has_bomb = False
        self.__flagged = False

    def flag(self) -> None: self.__flagged = True
    def flagged(self) -> bool: return self.__flagged
    def unflag(self) -> None: self.__flagged = False

    def reveal(self) -> None: self.__revealed = True
    def revealed(self) -> bool: return self.__revealed

    def setBomb(self) -> None: self.__has_bomb = True
    def hasBomb(self) -> bool: return self.__has_bomb
    def getBombCount(self) -> int: return self.__n_surrounding_bombs
    def increaseBombCount(self) -> None: self.__n_surrounding_bombs += 1
    def decreaseBombCount(self) -> None: self.__n_surrounding_bombs -= 1


class Game:
    def __init__(self, board_size: int = 5, bomb_count: int = 10) -> None:
        self.__board = [ [ BoardTile() for _ in range(self.board_size) ] for _ in range(self.board_size) ]
        self.__first_move = True
        self.__revealed_tiles = 0
        self.__safe_tiles = board_size ** 2 - bomb_count

        self.board_size: int = board_size
        self.bomb_count = bomb_count
        self.available_flags = bomb_count
        self.bombs_locations = []

    def __coordsValid(self, row: int, col: int) -> bool:
        input_valid: bool = \
            (row >= 0 and row < self.board_size) and \
            (col >= 0 and col < self.board_size)
        return input_valid

    def __placeBombs(self, safe_row: int, safe_col: int) -> None:
        valid_cells = []

        for row in range(self.board_size):
            for col in range(self.board_size):
                if abs(row - safe_row) <= 2 and abs(col - safe_col) <= 2:
                    continue
                valid_cells.append((row, col))

        if self.bomb_count > len(valid_cells):
            raise ValueError("Too many bombs for board size and safe zone.")

        random.shuffle(valid_cells)
        bombs = valid_cells[:self.bomb_count]

        for row, col in bombs:
            self.__board[row][col].setBomb()

        self.bombs_locations = bombs

    def __placeNumbers(self) -> None:
        for y_bomb, x_bomb in self.bombs_locations:
            for dy, dx in DELTA_PAIRS:
                y_new: int = y_bomb + dy
                x_new: int = x_bomb + dx
                coord_is_valid: bool = self.__coordsValid(y_new, x_new)
                if (coord_is_valid):
                    tile = self.__board[y_new][x_new]
                    tile.increaseBombCount()

    def printBoardWithMines(self) -> None:
        for row in self.__board:
            for tile in row[:-1]:
                print('   ' if not tile.hasBomb() else '[B]', end='')
            print('   ' if not row[-1].hasBomb() else '[B]')

    def printBoardForPlayer(self) -> None:
        print(' -', end='')
        [ print(f'-{i}-', end='') for i in range(self.board_size) ]
        print('-')
        for row_index in range(self.board_size):
            print(f'{row_index}|', end='')
            row = self.__board[row_index]
            for tile in row:
                if tile.revealed():
                    bomb_count = tile.getBombCount()
                    print(f"[{' ' if bomb_count==0 else bomb_count}]", end='')
                elif tile.flagged():
                    print(f'[F]', end='')
                else:
                    print('   ', end='')
            print('|')
        print(' -', end='')
        [ print('---', end='') for _ in range(self.board_size) ]
        print('-')

    def __checkCell(self, row: int, col: int) -> CustomNotif:
        input_valid: bool = self.__coordsValid(row, col)
        if (not input_valid):
            print('Invalid input!')
            return CustomNotif.INVALID_COORDINATES
        
        tile = self.__board[row][col]
        tile_has_bomb = tile.hasBomb()
        if (tile_has_bomb):
            return CustomNotif.FOUND_BOMB
        else: return CustomNotif.NO_BOMB

    def __revealSafeSpace(self, row: int, col: int) -> CustomNotif:
        input_valid: bool = self.__coordsValid(row, col)
        if (not input_valid):
            print('Invalid input!')
            return CustomNotif.INVALID_COORDINATES

        stack: list[tuple[int, int]] = [(row, col)]
        while stack:
            y, x = stack.pop()
            current_tile = self.__board[y][x]
            if current_tile.revealed(): pass
            current_tile.reveal()
            self.__revealed_tiles += 1

            if (current_tile.getBombCount() > 0): continue

            for dy, dx in DELTA_PAIRS:
                y_new: int = y + dy
                x_new: int = x + dx
                new_coord_is_valid: bool = self.__coordsValid(y_new, x_new)
                if (new_coord_is_valid):
                    neighbor_tile = self.__board[y_new][x_new]
                    can_reveal = (
                        not neighbor_tile.flagged() and
                        not neighbor_tile.hasBomb() and
                        not neighbor_tile.revealed()
                    )
                    if (can_reveal): stack.append((y_new, x_new))

        return CustomNotif.VALID_COORDINATES

    def revealTile(self, row: int, col: int) -> CustomNotif:
        if self.__first_move:
            self.__placeBombs(row, col)
            self.__placeNumbers()
            self.__first_move = False

        tile_check_result = self.__checkCell(row, col)
        if (not tile_check_result == CustomNotif.NO_BOMB):
            return tile_check_result
        reveal_tiles_result = self.__revealSafeSpace(row, col)
        return reveal_tiles_result

    def flag(self, row: int, col: int) -> CustomNotif:
        input_valid = self.__coordsValid(row, col)
        if (not input_valid):
            return CustomNotif.INVALID_COORDINATES

        if (self.available_flags <= 0):
            return CustomNotif.OUT_OF_FLAG

        tile = self.__board[row][col]
        if (tile.flagged()): 
            tile.unflag()
            self.available_flags += 1
            return CustomNotif.TILE_UNFLAGGED

        tile.flag()
        self.available_flags -= 1
        return CustomNotif.TILE_FLAGGED

    def checkWin(self) -> bool:
        return self.__revealed_tiles == self.__safe_tiles


class Agent:
    def __init__(self) -> None:
        pass
