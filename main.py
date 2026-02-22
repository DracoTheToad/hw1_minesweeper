from classes import *

def main():
    game = Game(10, 30)
    game.printBoardForPlayer()
    game.revealTile(2, 2)
    game.flag(10-1, 10-1)
    game.printBoardForPlayer()


if __name__ == "__main__":
    main()
