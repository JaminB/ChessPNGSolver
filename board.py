import sys
import typing
import autopy

from PIL import Image

import imagesearch

scale = autopy.screen.scale()

BoardInstance = typing.TypeVar('BoardInstance', bound='Board')

marker_map = [
    ('markers/edge-top-left.png', 'markers/edge-bottom-right.png', 'normal'),
    ('markers/edge-top-left-2.png', 'markers/edge-bottom-right-2.png', 'normal'),
    ('markers/edge-top-left-3.png', 'markers/edge-bottom-right-3.png', 'normal'),
    ('markers/edge-top-left-4.png', 'markers/edge-bottom-right-4.png', 'normal'),
    ('markers/edge-top-left-5.png', 'markers/edge-bottom-right-5.png', 'normal'),
    ('markers/edge-top-left-6.png', 'markers/edge-bottom-right-6.png', 'normal'),
    ('markers/edge-top-left-flipped.png', 'markers/edge-bottom-right-flipped.png', 'flipped'),
    ('markers/edge-top-left-flipped-2.png', 'markers/edge-bottom-right-flipped-2.png', 'flipped'),
    ('markers/edge-top-left-flipped-3.png', 'markers/edge-bottom-right-flipped-3.png', 'flipped'),
    ('markers/edge-top-left-flipped-4.png', 'markers/edge-bottom-right-flipped-4.png', 'flipped'),
    ('markers/edge-top-left-flipped-5.png', 'markers/edge-bottom-right-flipped-5.png', 'flipped'),
    ('markers/edge-top-left-flipped-6.png', 'markers/edge-bottom-right-flipped-6.png', 'flipped')
]


def get_png_position_on_screen(png_path: str, precision=0.92):
    """
    Returns the coordinates of a png found within the current screen shot, taken at the time of this function call

    :param png_path: The string, absolute path to the png file to search within the current screen
    :param precision: The accuracy in which the match must be made [default: 94% - .94]
    :return: The x, y coordinates of the top left corner of the first match
    """
    pos = imagesearch.imagesearch(png_path, precision=precision)
    return pos[0]/scale, pos[1]/scale


def get_board() -> BoardInstance:
    """
    Locate a chess board on the screen, create an instance of Board class from it, with virtual representations of
    position and pieces as well as their corresponding positions
    :return: An instance of the board from the current screen
    """
    def get_edges(top_left_png, bottom_right_png):
        edge_bottom_right_coords = get_png_position_on_screen(bottom_right_png, precision=.98)
        edge_top_left_coords = get_png_position_on_screen(top_left_png, precision=.98)
        return edge_top_left_coords, edge_bottom_right_coords

    def swap_marker_priorities(pos1, pos2):
        # popping both the elements from list
        first_ele = marker_map.pop(pos1)
        second_ele = marker_map.pop(pos2 - 1)

        # inserting in each others positions
        marker_map.insert(pos1, second_ele)
        marker_map.insert(pos2, first_ele)

    board = None
    for i, map in enumerate(marker_map):
        top_marker, bottom_marker, orientation = map
        top, bottom = get_edges(top_marker, bottom_marker)
        print('Trying Marker Set {} - {}'.format(i + 1, orientation))
        try:
            board = Board((top, bottom), flipped=orientation == 'flipped')
            swap_marker_priorities(0, i)
            print('Used Marker Set {}'.format(i + 1))
            break
        except InvalidBoardError:
            continue
    return board


def test_read_board():
    new_game_board_map = {
        'a1': ('rook', 'white'),
        'b1': ('knight', 'white'),
        'c1': ('bishop', 'white'),
        'd1': ('queen', 'white'),
        'e1': ('king', 'white'),
        'f1': ('bishop', 'white'),
        'g1': ('knight', 'white'),
        'h1': ('rook', 'white'),
        'a8': ('rook', 'black'),
        'b8': ('knight', 'black'),
        'c8': ('bishop', 'black'),
        'd8': ('queen', 'black'),
        'e8': ('king', 'black'),
        'f8': ('bishop', 'black'),
        'g8': ('knight', 'black'),
        'h8': ('rook', 'black')
    }
    board = get_board()
    columns = [
        '8', '7', '6', '5', '4', '3', '2', '1'
    ]
    rows = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    for row in rows:
        for column in columns:
            position = getattr(board, row + column)
            if column in ['1', '8']:
                if not position.piece:
                    print('Error: Could not locate {} at {}'.format(new_game_board_map[position.position],
                                                                    position.position), file=sys.stderr)
                elif position.piece.name != new_game_board_map[position.position][0] or \
                    position.piece.color != new_game_board_map[position.position][1]:
                    print('Error: Found {} at {} - expected - {}'.format(position.piece, position.position,
                                                                         new_game_board_map[position.position]),
                          file=sys.stderr)
            elif column == '2':
                if not position.piece:
                    print('Error: Could not locate {} at {}'.format(('pawn', 'white'),
                                                                    position.position), file=sys.stderr)
                elif position.piece.name != 'pawn' or position.piece.color != 'white':
                    print('Error: Found {} at {} - expected - {}'.format(position.piece, position.position,
                                                                         ('pawn', 'white')))
            elif column == '7':
                if not position.piece:
                    print('Error: Could not locate {} at {}'.format(('pawn', 'black'),
                                                                    position.position), file=sys.stderr)
                elif position.piece.name != 'pawn' or position.piece.color != 'black':
                    print('Error: Found {} at {} - expected - {}'.format(position.piece, position.position,
                                                                         ('pawn', 'black')), file=sys.stderr)
            else:
                if position.piece:
                    print('Error: Unexpected piece {} found at {}'.format(position.piece, position.position),
                          file=sys.stderr)
    print("Flipped: {}".format(board.flipped))
    print(board.to_fen_string())


class InvalidBoardError(Exception):

    def __init__(self, coordinates: typing.Tuple[typing.Tuple]):
        self.coordinates = coordinates
        msg = 'Invalid Board/No Board Found - Try increasing/decreasing the size of the board on screen. ' \
              'Detected Coordinates: [{}]'.format(self.coordinates)
        super(InvalidBoardError, self).__init__(msg)


class Board:
    """
    Represents the chess board
    """

    EDGE_TOP_LEFT_CORRECT_X = 10
    EDGE_TOP_LEFT_CORRECT_Y = 7

    def __init__(self, dimensions: typing.Tuple, flipped=False, save_sample_of_board=True):
        """
        :param dimensions: (x1, y1) of top left corner (x2, y2) of bottom right
        """
        self.save_sample_of_board = save_sample_of_board
        self.flipped = flipped

        # From whites POV (standard board orientation)
        self.columns = ['8', '7', '6', '5', '4', '3', '2', '1']
        self.rows = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

        # Or use flipped orientation
        if flipped:
            self.columns.reverse()
            self.rows.reverse()
        self.dimensions = dimensions
        self.unit_pixels = 0
        self.white_to_move = True
        self.last_move = None
        self.a1, self.a2, self.a3, self.a4, self.a5, self.a6, self.a7, self.a8 = None, None, None, None, None, None, None, None
        self.b1, self.b2, self.b3, self.b4, self.b5, self.b6, self.b7, self.b8 = None, None, None, None, None, None, None, None
        self.c1, self.c2, self.c3, self.c4, self.c5, self.c6, self.c7, self.c8 = None, None, None, None, None, None, None, None
        self.d1, self.d2, self.d3, self.d4, self.d5, self.d6, self.d7, self.d8 = None, None, None, None, None, None, None, None
        self.e1, self.e2, self.e3, self.e4, self.e5, self.e6, self.e7, self.e8 = None, None, None, None, None, None, None, None
        self.f1, self.f2, self.f3, self.f4, self.f5, self.f6, self.f7, self.f8 = None, None, None, None, None, None, None, None
        self.g1, self.g2, self.g3, self.g4, self.g5, self.g6, self.g7, self.g8 = None, None, None, None, None, None, None, None
        self.h1, self.h2, self.h3, self.h4, self.h5, self.h6, self.h7, self.h8 = None, None, None, None, None, None, None, None
        self.evaluate()

    def eval_latest_move(self):
        most_matched_pixels = 0
        for row in self.rows:
            for column in self.columns:
                position = getattr(self, row + column)
                if position.piece and position.move_matched_pixels > most_matched_pixels:
                    most_matched_pixels = position.move_matched_pixels
                    # print(most_matched_pixels, position.position, str(position.piece)) # Debug
                    self.last_move = (str(position.piece), position.position)
                    if position.piece.color == 'black':
                        self.white_to_move = True
                    else:
                        self.white_to_move = False

    def evaluate(self) -> None:
        """
        Adjust the board so that every piece fits inside a unit by unit square; cache eache pieces png;
        derive the value of unit (side [in pixels] of a single square)
        """
        length_pixels = abs(self.dimensions[1][1] - self.dimensions[0][1])
        x1, y1, x2, y2 = self.dimensions[0][0], self.dimensions[0][1], self.dimensions[1][0], self.dimensions[1][1]
        unit = length_pixels/7.6
        """
        if self.save_sample_of_board:
            autopy.bitmap.capture_screen((
                (x1, y1),
                (unit * 8, unit * 8),
            )).save('board-found.png')
        """
        self.unit_pixels = unit
        if x1 < 0 or x2 < 0 or y1 < 0 or y2 < 0:
            raise InvalidBoardError(self.dimensions)
        for i, row in enumerate(self.rows):
            for j, column in enumerate(self.columns):
                coords = (self.dimensions[0][0] + Board.EDGE_TOP_LEFT_CORRECT_X + (i * self.unit_pixels)), \
                         (self.dimensions[0][1] + Board.EDGE_TOP_LEFT_CORRECT_Y + (j * self.unit_pixels))
                setattr(self, row + column, Position(coords[0], coords[1], self.unit_pixels, row + column))

        self.eval_latest_move()

    def white_can_castle_kingside(self):
        if self.h1.piece and self.h1.piece.name == 'rook' and self.e1.piece and self.e1.piece.name == 'king':
            return True
        return False

    def white_can_castle_queenside(self):
        if self.a1.piece and self.a1.piece.name == 'rook' and self.e1.piece and self.e1.piece.name == 'king':
            return True
        return False

    def black_can_castle_kingside(self):
        if self.h8.piece and self.h8.piece.name == 'rook' and self.e8.piece and self.e8.piece.name == 'king':
            return True
        return False

    def black_can_castle_queenside(self):
        if self.a8.piece and self.a8.piece.name == 'rook' and self.e8.piece and self.e8.piece.name == 'king':
            return True
        return False

    def to_fen_string(self):
        fen_name_map = {
            'white': {
                'rook': 'R',
                'knight': 'N',
                'bishop': 'B',
                'queen': 'Q',
                'king': 'K',
                'pawn': 'P'
            },
            'black': {
                'rook': 'r',
                'knight': 'n',
                'bishop': 'b',
                'queen': 'q',
                'king': 'k',
                'pawn': 'p'
            }
        }
        eval_rows = [
            ['a8', 'b8', 'c8', 'd8', 'e8', 'f8', 'g8', 'h8'],
            ['a7', 'b7', 'c7', 'd7', 'e7', 'f7', 'g7', 'h7'],
            ['a6', 'b6', 'c6', 'd6', 'e6', 'f6', 'g6', 'h6'],
            ['a5', 'b5', 'c5', 'd5', 'e5', 'f5', 'g5', 'h5'],
            ['a4', 'b4', 'c4', 'd4', 'e4', 'f4', 'g4', 'h4'],
            ['a3', 'b3', 'c3', 'd3', 'e3', 'f3', 'g3', 'h3'],
            ['a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2'],
            ['a1', 'b1', 'c1', 'd1', 'e1', 'f1', 'g1', 'h1'],
        ]
        fen_string = ''
        for row in eval_rows:
            row_string = ''
            blank_count = 0
            for pos in row:
                position = getattr(self, pos)
                if position.piece:
                    if blank_count > 0:
                        row_string += str(blank_count)
                        blank_count = 0
                    row_string += fen_name_map[position.piece.color][position.piece.name]
                else:
                    blank_count += 1
            if blank_count > 0:
                row_string += str(blank_count)
            fen_string += row_string + '/'
        if self.white_to_move:
            fen_string = fen_string.strip('/') + ' w '
        else:
            fen_string = fen_string.strip('/') + ' b '
        at_least_one_castle = False
        if self.white_can_castle_kingside():
            fen_string += 'K'
            at_least_one_castle = True
        if self.white_can_castle_queenside():
            fen_string += 'Q'
            at_least_one_castle = True
        if self.black_can_castle_kingside():
            fen_string += 'k'
            at_least_one_castle = True
        if self.black_can_castle_queenside():
            fen_string += 'q'
            at_least_one_castle = True
        if not at_least_one_castle:
            fen_string += '-'

        return fen_string

    def to_json(self) -> typing.List:
        """
        Get a JSON serializable representation of the current state of the board

        A dictionary representation of pieces on the board with their screen coordinates included
        :return: A dictionary containing the name of the piece, its color, coordinates on board, and position on screen.
        """
        pieces = []
        for row in self.rows:
            for column in self.columns:
                position = getattr(self, row + column)
                if position.piece:
                    pieces.append(
                        {
                            'piece': position.piece.name,
                            'color': position.piece.color,
                            'coordinates': position.position,
                            'screen': (position.x, position.y)
                        }
                    )
        return pieces


class Piece:
    """
    Represents a single piece on the board
    """
    def __init__(self, name, color):
        self.name = name
        self.color = color

    def __str__(self):
        return '{} ({})'.format(self.name, self.color)


class Position:
    """
    Represents a position on the board
    """
    def __init__(self, x, y, size, position_string):
        self.x = x
        self.y = y
        self.size = size
        self.piece = None
        self.position = position_string
        self.move_matched_pixels = 0
        cached_png = self.get_png()
        cached_png.save('cache/{}.png'.format(self.position))
        self.cached_png_path = 'cache/{}.png'.format(self.position)
        self.cached_png = Image.open(self.cached_png_path)
        self.eval_position()

    def get_square_color(self) -> str:
        """
        Get the color of a square for a given chess coordinate (E.G a1, b1, h1, h8)
        :return: Either 'white' or 'black'
        """
        row_map = {
            'a': 1,
            'b': 2,
            'c': 3,
            'd': 4,
            'e': 5,
            'f': 6,
            'g': 7,
            'h': 8
        }
        if row_map[self.position[0]] % 2 == 0:
            if int(self.position[1]) % 2 == 0:
                return 'black'
            else:
                return 'white'
        else:
            if int(self.position[1]) % 2 == 0:
                return 'white'
            else:
                return 'black'

    def get_png(self) -> autopy.bitmap.Bitmap:
        """
        Gets the bitmap of the current position of the coordinates
        :return: A bitmap object representing the coordinates of the position
        """
        bitmap = autopy.bitmap.capture_screen(((self.x, self.y), (self.size, self.size)))
        return bitmap

    def eval_position(self) -> None:
        """
        Evaluates the position; determines if any pieces exist on it; if so associates the piece with the position,
        storing the value in Position.piece
        """
        maps = [
            ('pawn', 'white', 'pieces/pawn-white-f.png'),
            ('pawn', 'white', 'pieces/pawn-white-t.png'),
            ('pawn', 'white', 'pieces/pawn-white-t2.png'),
            ('pawn', 'white', 'pieces/pawn-white-t3.png'),
            ('pawn', 'white', 'pieces/pawn-white-b.png'),
            ('pawn', 'white', 'pieces/pawn-white-l.png'),
            ('pawn', 'white', 'pieces/pawn-white-r.png'),
            ('pawn', 'black', 'pieces/pawn-black-f.png'),
            ('pawn', 'black', 'pieces/pawn-black-t.png'),
            ('pawn', 'black', 'pieces/pawn-black-t2.png'),
            ('pawn', 'black', 'pieces/pawn-black-b.png'),
            ('pawn', 'black', 'pieces/pawn-black-l.png'),
            ('pawn', 'black', 'pieces/pawn-black-r.png'),
            ('rook', 'white', 'pieces/rook-white-f.png'),
            ('rook', 'white', 'pieces/rook-white-t.png'),
            ('rook', 'white', 'pieces/rook-white-t2.png'),
            ('rook', 'white', 'pieces/rook-white-b.png'),
            ('rook', 'white', 'pieces/rook-white-l.png'),
            ('rook', 'white', 'pieces/rook-white-l2.png'),
            ('rook', 'white', 'pieces/rook-white-r.png'),
            ('rook', 'white', 'pieces/rook-white-r2.png'),
            ('rook', 'black', 'pieces/rook-black-f.png'),
            ('rook', 'black', 'pieces/rook-black-t.png'),
            ('rook', 'black', 'pieces/rook-black-t2.png'),
            ('rook', 'black', 'pieces/rook-black-b.png'),
            ('rook', 'black', 'pieces/rook-black-l.png'),
            ('rook', 'black', 'pieces/rook-black-r.png'),
            ('knight', 'white', 'pieces/knight-white-f.png'),
            ('knight', 'white', 'pieces/knight-white-t.png'),
            ('knight', 'white', 'pieces/knight-white-t2.png'),
            ('knight', 'white', 'pieces/knight-white-t3.png'),
            ('knight', 'white', 'pieces/knight-white-b.png'),
            ('knight', 'white', 'pieces/knight-white-b2.png'),
            ('knight', 'white', 'pieces/knight-white-l.png'),
            ('knight', 'white', 'pieces/knight-white-l2.png'),
            ('knight', 'white', 'pieces/knight-white-r.png'),
            ('knight', 'white', 'pieces/knight-white-r2.png'),
            ('knight', 'black', 'pieces/knight-black-f.png'),
            ('knight', 'black', 'pieces/knight-black-t.png'),
            ('knight', 'black', 'pieces/knight-black-t2.png'),
            ('knight', 'black', 'pieces/knight-black-b.png'),
            ('knight', 'black', 'pieces/knight-black-b2.png'),
            ('knight', 'black', 'pieces/knight-black-b3.png'),
            ('knight', 'black', 'pieces/knight-black-l.png'),
            ('knight', 'black', 'pieces/knight-black-r.png'),
            ('knight', 'black', 'pieces/knight-black-r2.png'),
            ('bishop', 'white', 'pieces/bishop-white-f.png'),
            ('bishop', 'white', 'pieces/bishop-white-t.png'),
            ('bishop', 'white', 'pieces/bishop-white-t2.png'),
            ('bishop', 'white', 'pieces/bishop-white-t3.png'),
            ('bishop', 'white', 'pieces/bishop-white-b.png'),
            ('bishop', 'white', 'pieces/bishop-white-l.png'),
            ('bishop', 'white', 'pieces/bishop-white-r.png'),
            ('bishop', 'black', 'pieces/bishop-black-f.png'),
            ('bishop', 'black', 'pieces/bishop-black-t.png'),
            ('bishop', 'black', 'pieces/bishop-black-b.png'),
            ('bishop', 'black', 'pieces/bishop-black-b2.png'),
            ('bishop', 'black', 'pieces/bishop-black-b3.png'),
            ('bishop', 'black', 'pieces/bishop-black-l.png'),
            ('bishop', 'black', 'pieces/bishop-black-r.png'),
            ('queen', 'white', 'pieces/queen-white-f.png'),
            ('queen', 'white', 'pieces/queen-white-t.png'),
            ('queen', 'white', 'pieces/queen-white-t2.png'),
            ('queen', 'white', 'pieces/queen-white-t3.png'),
            ('queen', 'white', 'pieces/queen-white-b.png'),
            ('queen', 'white', 'pieces/queen-white-b2.png'),
            ('queen', 'white', 'pieces/queen-white-b3.png'),
            ('queen', 'white', 'pieces/queen-white-l.png'),
            ('queen', 'white', 'pieces/queen-white-r.png'),
            ('queen', 'white', 'pieces/queen-white-r2.png'),
            ('queen', 'black', 'pieces/queen-black-f.png'),
            ('queen', 'black', 'pieces/queen-black-t.png'),
            ('queen', 'black', 'pieces/queen-black-t2.png'),
            ('queen', 'black', 'pieces/queen-black-b.png'),
            ('queen', 'black', 'pieces/queen-black-l.png'),
            ('queen', 'black', 'pieces/queen-black-l2.png'),
            ('queen', 'black', 'pieces/queen-black-r.png'),
            ('king', 'white', 'pieces/king-white-f.png'),
            ('king', 'white', 'pieces/king-white-t.png'),
            ('king', 'white', 'pieces/king-white-t2.png'),
            ('king', 'white', 'pieces/king-white-t3.png'),
            ('king', 'white', 'pieces/king-white-b.png'),
            ('king', 'white', 'pieces/king-white-b2.png'),
            ('king', 'white', 'pieces/king-white-l.png'),
            ('king', 'white', 'pieces/king-white-l2.png'),
            ('king', 'white', 'pieces/king-white-r.png'),
            ('king', 'white', 'pieces/king-white-r2.png'),
            ('king', 'white', 'pieces/king-white-r3.png'),
            ('king', 'black', 'pieces/king-black-f.png'),
            ('king', 'black', 'pieces/king-black-t.png'),
            ('king', 'black', 'pieces/king-black-t2.png'),
            ('king', 'black', 'pieces/king-black-b.png'),
            ('king', 'black', 'pieces/king-black-l.png'),
            ('king', 'black', 'pieces/king-black-r.png')
        ]
        for map in maps:
            name, color, path = map
            try:
                coords = imagesearch.imagesearcharea(path, 0, 0,
                                                     self.size * scale, self.size * scale, precision=.8, im=self.cached_png)
                if coords != [-1, -1]:
                    self.piece = Piece(name, color)
                    bitmap = autopy.bitmap.Bitmap.open(self.cached_png_path)
                    last_move_color_match_1 = bitmap.count_of_color((246, 246, 145), .03)
                    last_move_color_match_2 = bitmap.count_of_color((190, 202, 95), .03)
                    last_move_color_match_3 = bitmap.count_of_color((222, 228, 96), .03)
                    last_move_color_match_4 = bitmap.count_of_color((250, 250, 126), .03)
                    self.move_matched_pixels = last_move_color_match_1 + last_move_color_match_2 + \
                                               last_move_color_match_3 + last_move_color_match_4
                    break
            except Exception as e:
                if 'matchTemplate' in str(e):
                    continue


if __name__ == '__main__':
    test_read_board()