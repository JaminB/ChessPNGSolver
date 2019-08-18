import time
import random
import chess.engine
import pyautogui
import board
pyautogui.FAILSAFE = False


class Game:

    def __init__(self):
        self.board = None
        self.position_cache = {}
        self.virtual_board = None

    def cache_positions(self):
        columns = [
            '8', '7', '6', '5', '4', '3', '2', '1'
        ]
        rows = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        for row in rows:
            for column in columns:
                position = getattr(self.board, row + column)
                self.position_cache[row+column] = position.x, position.y

    def create_virtual_board(self):
        self.virtual_board = chess.Board(self.board.to_fen_string())

    def get_next_move(self):
        engine = chess.engine.SimpleEngine.popen_uci('engines/stockfish-10-64')
        move = str(engine.play(self.virtual_board, chess.engine.Limit(time=2.00)).move)
        engine.quit()
        return move[0] + str(move[1]), move[2] + str(move[3])

    def move(self, start_pos, dest_pos):
        center_of_start_pos = self.position_cache[start_pos][0] + self.board.unit_pixels/2, \
                              self.position_cache[start_pos][1] + self.board.unit_pixels/2

        center_of_dest_pos = self.position_cache[dest_pos][0] + self.board.unit_pixels/2, \
                              self.position_cache[dest_pos][1] + self.board.unit_pixels/2
        pyautogui.moveTo(center_of_start_pos, duration=.1, tween=pyautogui.easeInOutQuad)
        pyautogui.click()
        pyautogui.dragTo(center_of_dest_pos, duration=.1, tween=pyautogui.linear)

    def start(self):
        while True:
            self.board = board.get_board()
            self.cache_positions()
            self.create_virtual_board()
            color_to_play = 'white'
            if not self.board.white_to_move:
                color_to_play = 'black'
            print('Last Move: {}'.format(self.board.last_move))
            print('Board State [{}]: {}'.format(color_to_play, self.board.to_fen_string()))
            start, dest = self.get_next_move()
            print('Moving: {} to {}'.format(str(getattr(self.board, start).piece), dest))
            self.move(start, dest)
            time.sleep(.01)
            pyautogui.click()
            time.sleep(random.randint(1, random.randint(5, 9)))
            if self.virtual_board.is_checkmate() or self.virtual_board.is_stalemate():
                break


if __name__ == '__main__':
    Game().start()