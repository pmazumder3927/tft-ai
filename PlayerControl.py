import pyautogui
import time
from Resources import Resources


class PlayerControl:
    def __init__(self):
        """
        self.action_sequence = []
        self.board = [None] * 21
        self.shop = [None] * 5
        self.items = [None] * 10
        """
        self.offset = (0, 0)
        self.resources = Resources()

    def offsetMove(self, x, y, duration=-1):
        if duration == -1:
            pyautogui.moveTo(x + self.offset[0], y + self.offset[1])
        else:
            pyautogui.moveTo(x + self.offset[0], y + self.offset[1], duration)

    def buyChampion(self, store_index):
        """
        Buys the nth champion from the left in the store.
        """
        self.offsetMove(578 + 201 * store_index, 1000)
        pyautogui.mouseDown()
        time.sleep(0.05)
        pyautogui.mouseUp()

    def sellChampion(self, bench_idx):
        """
        Sells the nth champion from the left on the bench.
        """
        self.offsetMove(420 + 122 * bench_idx, 775)
        pyautogui.press("e")

    def reroll(self):
        """
        Presses the reroll button via default hotkey.
        """
        pyautogui.press("d")
        self.resources.increaseGoldBy(-2)

    def levelUp(self):
        """
        Presses the level up button via default hotkey.
        """
        pyautogui.press("f")
        self.resources.increaseXpBy(4)

    def boardIndexToPosition(self, board_index):
        """
        Translates board index (0-20) to screen position in 1920x1080 resolution.
        """
        if board_index < 7:
            return (540 + 145 * board_index, 667)
        elif board_index < 14:
            return (493 + 138 * (board_index % 7), 573)
        else:
            return (575 + 133 * (board_index % 7), 488)

    def placeChampOnBoard(self, bench_index, board_index):
        """
        Places champion from given bench position to given board position.
        """
        self.offsetMove(420 + 122 * bench_index, 775)
        board_position = self.boardIndexToPosition(board_index)
        pyautogui.mouseDown()
        self.offsetMove(board_position[0], board_position[1], duration=0.15)
        pyautogui.mouseUp()

    def placeChampOnBench(self, board_index, bench_index):
        """
        Places champion from given board position to given bench position.
        """
        pos = self.boardIndexToPosition(board_index)
        self.offsetMove(pos[0], pos[1])
        pyautogui.mouseDown()
        self.offsetMove(420 + 122 * bench_index, 775, duration=0.15)
        pyautogui.mouseUp()

    def reorderChampOnBench(self, bench_index1, bench_index2):
        """
        Places champion from given bench position to another given bench position.
        """
        self.offsetMove(420 + 122 * bench_index1, 775)
        pyautogui.mouseDown()
        self.offsetMove(420 + 122 * bench_index2, 775, duration=0.15)
        pyautogui.mouseUp()

    def reorderChampOnBoard(self, board_index1, board_index2):
        """
        Places champion from given board position to another given board position.
        """
        pos = self.boardIndexToPosition(board_index1)
        self.offsetMove(pos[0], pos[1])
        board_position = self.boardIndexToPosition(board_index2)
        pyautogui.mouseDown()
        self.offsetMove(board_position[0], board_position[1], duration=0.15)

    def setOffset(self, off):
        self.offset = off
