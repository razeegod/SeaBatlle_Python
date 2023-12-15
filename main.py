import random
from random import randint
class SeaBattleException(Exception):
    pass

class BoardOutException(SeaBattleException):
    def __str__(self):
        return f"Вы пытаетесь выстрелить за пределы игрового поля!"

class BoardUsedException(SeaBattleException):
    def __str__(self):
        return f"Эта клетка уже занята!"

class BoardShootedException(SeaBattleException):
    def __str__(self):
        return f"Вы уже стреляли в эту клетку!"

class Dot:
    def __init__(self, coor_x, coor_y):
        self.coor_x = coor_x
        self.coor_y = coor_y

    def __eq__(self, other):
        return self.coor_x == other.coor_x and self.coor_y == other.coor_y

    def __str__(self):
        return f"Dot: x = {self.coor_x}, y = {self.coor_y}"

class Ship:
    def __init__(self, size, g_dot, nose_dot):
        self.size = size
        self.g_dot = g_dot
        self.health_count = size
        self.nose_dot = nose_dot
        self.dots_list = self.get_dots()

    def get_dots(self):
        dots = []
        for i in range(self.size):
            cur_x = self.g_dot.coor_x
            cur_y = self.g_dot.coor_y

            if self.nose_dot == 0:
                cur_x += i
            elif self.nose_dot == 1:
                cur_y += i

            dots.append(Dot(cur_x, cur_y))

        return dots

    def shooted(self, dot):
        return dot in self.dots_list

class Board:
    def __init__(self, size=6, hid=False):
        self.size = size
        self.board = [['О'] * size for _ in range(size)]
        self.ships_list = []
        self.hid = hid
        self.busy_dots = []
        self.dead_ships_count = 0

    def win_check(self):
        return self.dead_ships_count == len(self.ships_list)

    def  add_ship(self, ship):
        for dot in ship.dots_list:
            if self.out(dot) or dot in self.busy_dots:
                raise BoardUsedException()
        for dot in ship.dots_list:
            self.board[dot.coor_x][dot.coor_y] = "■"
            self.busy_dots.append(dot)

        self.ships_list.append(ship)
        self.contour(ship, status=False)

    def contour(self, ship, status=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]

        for dot in ship.dots_list:
            for dot_x, dot_y in near:
                current = Dot(dot.coor_x + dot_x, dot.coor_y + dot_y)
                if not (self.out(current)) and current not in self.busy_dots:
                    if status:
                        self.board[current.coor_x][current.coor_y] = "."
                    self.busy_dots.append(current)

    def __str__(self):
        field = "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.board):
            field += f"\n{i+1} | " + " | ".join(row) + " |"

        if self.hid:
            field = field.replace("■", "O")
        return field

    def out(self, dot):
        return not ((0 <= dot.coor_x < self.size) and (0 <= dot.coor_y < self.size))

    def shot(self, dot):
        if self.out(dot):
            raise BoardOutException()
        elif dot in self.busy_dots:
            raise BoardUsedException()

        self.busy_dots.append(dot)

        for ship in self.ships_list:
            if ship.shooted(dot):
                ship.health_count -= 1
                self.board[dot.coor_x][dot.coor_y] = "X"
                if ship.health_count == 0:
                    self.dead_ships_count += 1
                    self.contour(ship, status=True)
                    print(f'Корабль уничтожен!')
                    return False
                else:
                    print("Корабль повреждён!")
                    return True
        self.board[dot.coor_x][dot.coor_y] = "М"
        print("Мимо!")
        return False
    def again(self):
        self.busy_dots = []

class Player:
    def __init__(self, board, enemy_board):
        self.board = board
        self.enemy_board = enemy_board

    def ask(self):
        pass

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy_board.shot(target)
                return repeat
            except SeaBattleException as e:
                print(e)

class AI(Player):
    def ask(self):
        dot = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход AI игрока: {dot.coor_x + 1} {dot.coor_y + 1}")
        return dot

class User(Player):
    def ask(self):
        while True:
            print("Ваш ход!")
            coordinates = input("Введите координаты: ").split()
            if len(coordinates) != 2:
                print("Введите 2 координаты!")
                continue
            x, y = coordinates

            if not (x.isdigit()) or not (y.isdigit()):
                print("Введите числа!")
                continue
            x, y = int(x), int(y)
            return Dot(x-1, y-1)

class Game:
    def __init__(self, size=6):
        self.size = size
        player_board = self.random_board()
        ai_player_board = self.random_board()
        ai_player_board.hid = True
        self.player = User(player_board, ai_player_board)
        self.ai_player = AI(ai_player_board, player_board)

    def try_board(self):
        ships_len = [3, 2, 2, 1, 1, 1, 1]
        attempts = 0
        board = Board(self.size)
        for length in ships_len:
            while True:
                attempts += 1
                if attempts >= 1500:
                    return None
                nose_dot = randint(0, 1)
                x = randint(0, self.size-1)
                y = randint(0, self.size-1)
                if nose_dot == 0 and x + length > self.size:
                    continue
                if nose_dot == 1 and y + length > self.size:
                    continue
                ship = Ship(length, Dot(x, y), nose_dot)
                try:
                    board.add_ship(ship)
                    break
                except BoardUsedException as e:
                    pass
        board.again()
        return board
    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board
    def great(self):
        print("=" * 30)
        print(f"""Добро пожаловать в "Морской бой"!""")
        print("=" * 30)
        print(f"""Правила игры: \nПобеждает тот, кто быстрее всех разгромит корабли противника\n
        Формат ввода: x y\n
        x - номер строки\n
        y - номер столбца""")

    def loop(self):
        motion = 0
        while True:
            print("=" * 30)
            print("Ваша доска: ")
            print(self.player.board)
            print("=" * 30)
            print("Доска компьютера: ")
            print(self.ai_player.board)
            print("=" * 30)

            if motion % 2 == 0:
                print("Ход пользователя")
                repeat = self.player.move()
                print("=" * 30)
            else:
                print("Ход компьютера")
                repeat = self.ai_player.move()
                print("=" * 30)

            if repeat:
                motion -= 1

            if self.player.board.win_check():
                print("=" * 30)
                print("Компьютер победил! \n" * 3)
                break
            if self.ai_player.board.win_check():
                print("=" * 30)
                print("Вы выиграли!\n" * 3)
                break
            motion += 1
    def start(self):
        self.great()
        self.loop()

game = Game()
game.start()
