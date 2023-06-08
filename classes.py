import random


class BoardException(Exception):
    pass


class OutException(BoardException):
    def __str__(self):
        return 'Введенная координата - за пределами доски'


class RepeatMoveException(BoardException):
    def __str__(self):
        return 'Повтор хода'


class WrongShipPosException(BoardException):
    pass


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Pos({self.x}, {self.y})'


class Ship:
    def __init__(self, size, first_pos, orientation):
        self.size = size
        self.first_pos = first_pos
        self.orientation = orientation
        self.health = size

    @property
    def positions(self):
        ship_positions = []
        for i in range(self.size):
            pos_x = self.first_pos.x
            pos_y = self.first_pos.y

            if self.orientation == 0:
                pos_x += i
            elif self.orientation == 1:
                pos_y += i
            ship_positions.append(Position(pos_x, pos_y))
        return ship_positions

    def damage(self, pos):
        return pos in self.positions


class Board:
    def __init__(self, is_hide=False, size=6):
        self.is_hide = is_hide
        self.size = size
        self.score = 0
        self.filling = []
        self.ships = []
        self.board_to_play = [['0'] * self.size for i in range(self.size)]

    def __str__(self):
        line = '   | ' + ' '.join([f'{i + 1} |' for i in range(self.size)])
        for i, row in enumerate(self.board_to_play):
            line += f"\n {i+1} | {' | '.join(row)} | "
            if self.is_hide:
                line = line.replace('\u2584', '0')
        return line

    def out_move(self, pos):
        return not (0 <= pos.x < self.size and 0 <= pos.y < self.size)

    def buffer(self, ship, destroyed=False):
        buffers = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        for pos in ship.positions:
            for pos_x, pos_y in buffers:
                point = Position(pos.x + pos_x, pos.y + pos_y)
                if not self.out_move(point) and pos not in self.filling:
                    if destroyed:
                        self.board_to_play[pos.x][pos.y] = '.'
                self.filling.append(point)

    def add_ship(self, ship):
        for pos in ship.positions:
            if self.out_move(pos) or pos in self.filling:
                raise WrongShipPosException()
        for pos in ship.positions:
            self.board_to_play[pos.x][pos.y] = '\u2584'
            self.filling.append(pos)
        self.ships.append(ship)
        self.buffer(ship)

    def shot(self, pos):
        if self.out_move(pos):
            raise OutException
        if pos in self.filling:
            raise RepeatMoveException
        self.filling.append(pos)
        for ship in self.ships:
            if ship.damage(pos):
                ship.health -= 1
                self.board_to_play[pos.x][pos.y] = 'X'
                if ship.health == 0:
                    self.score += 1
                    self.buffer(ship, True)
                    print('Потопил!')
                    return False
                else:
                    print('Ранил!')
                    return True
        self.board_to_play[pos.x][pos.y] = 'T'
        print('Мимо...')
        return False

    def refilling(self):
        self.filling = []

    def defeat(self):
        return self.score == len(self.ships)


class Gamer:
    def __init__(self, board, enemy_board):
        self.board = board
        self.enemy_board = enemy_board

    def ask(self):
        raise NotImplementedError

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy_board.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Gamer):
    def ask(self):
        pos = Position(random.randint(0, 5), random.randint(0, 5))
        print(f'ИИ сделал ход: {pos.x + 1} - {pos.y + 1}')
        return pos


class Player(Gamer):
    def ask(self):
        while True:
            x_y = input('Введите координаты точки через пробел, сначала "х" потом "у" ').split()
            if len(x_y) != 2:
                print('Введите только 2 значения через пробел')
                continue
            x, y = x_y
            if not x.isdigit() or not y.isdigit():
                print('Введите целые числа')
                continue
            x, y = int(x), int(y)
            return Position(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size

        player_board = self.random_board()
        ai_board = self.random_board()
        ai_board.is_hide = True
        self.player = Player(player_board, ai_board)
        self.AI = AI(ai_board, player_board)

    def greeting(self):
        print(" ---------------------------")
        print("       Приветствуем Вас   ")
        print("           в игре        ")
        print("         Морской Бой     ")
        print(" ---------------------------")
        print("    формат ввода: 'x' и 'y'")
        print("    где 'x' - номер строки")
        print("     а 'y' - номер столбца ")
        print(" ---------------------------")
        print("     Обозначение клеток: ")
        print("         Т - промах      ")
        print("       Х - попадание     ")
        print("    0 - неиспользованная ")
        print(" ---------------------------")

    def create_board(self):
        lengths = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        count = 0
        for length in lengths:
            while True:
                count += 1
                if count >= 2000:
                    return None
                ship = Ship(length, Position(random.randint(0, self.size),
                            random.randint(0, self.size)),
                            random.randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except WrongShipPosException:
                    pass
        board.refilling()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.create_board()
        return board

    def window(self):
        print()
        print('         Ваша доска')
        print(' ---------------------------')
        print(self.player.board)
        print()
        print('          Доска ИИ')
        print(' ---------------------------')
        print(self.AI.board)
        print()

    def game_logic(self):
        i = 0
        while True:
            self.window()
            if i % 2 == 0:
                print('      Ваш ход')
                repeat = self.player.move()
            else:
                print('      Ход ИИ')
                repeat = self.AI.move()
            if repeat:
                i -= 1
            if self.player.board.defeat():
                print()
                self.window()
                print()
                print('К сожалению, Вы проиграли!!!')
                break
            if self.AI.board.defeat():
                print()
                self.window()
                print()
                print('Вы победили!!!')
                break
            i += 1

    def start(self):
        self.greeting()
        self.game_logic()


