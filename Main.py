import time

import pyautogui
import win32gui

from Field import Field
from PlayerControl import PlayerControl
from ScreenInterpreter import ScreenInterpreter


info_reader = ScreenInterpreter()


def testStoreVision():
    "Reads champions in store from screenshot, adds them to board, then prints synergies."
    print("Reading...")
    info_reader.readStore()
    print("Identified champs from store: " + str(info_reader.getStore()))
    print("Identified gold total: " + str(info_reader.getGold()))

def scanBoard(pc):
    for i in [20, 19]:
        pos = pc.boardIndexToPosition(i)
        pyautogui.mouseDown(button='right', x=pos[0] + offset[0], y=pos[1] + offset[1])
        pyautogui.mouseUp(button='right')
        #pyautogui.click(pos[0] + offset[0], pos[1] + offset[1], button='right', interval=0.15, clicks=2)
def scanBench(pc):
    for i in range(9):
        pos = (420 + 122 * i, 775)
        pyautogui.mouseDown(button='right', x=pos[0] + offset[0], y=pos[1] + offset[1])
        pyautogui.mouseUp(button='right')
        champion = info_reader.readChampion(pos[0] + offset[0], pos[1] + offset[1] - 120, pos[0] + offset[0] + 400, pos[1] + offset[1] + 150)
        field.addChampionToBench(champion, i)
    print(field.getBoardRepresentation())
    print(field.getBenchRepresentation())
    print(field)
    field.parseShop(info_reader.getStore())
    print(field.shop)
def testManeuvering():
    "Tests moving champions around."
    print("Maneuvering...")
    pc = PlayerControl()
    pc.setOffset(offset)
    scanBench(pc)
    """
    pc.placeChampOnBoard(0, 18)
    pc.reorderChampOnBoard(18, 10)
    pc.reorderChampOnBoard(10, 11)
    pc.placeChampOnBench(11, 1)
    pc.reorderChampOnBench(1, 6)
    pc.reorderChampOnBench(6, 6)
    pc.placeChampOnBoard(6, 14)
    pc.reorderChampOnBoard(14, 6)
    pc.buyChampion(1)
    pc.buyChampion(2)
    """
def buyOut():
    "Buys all chmapions in store."
    pc = PlayerControl()
    for i in range(5):
        pc.buyChampion(i)
        time.sleep(0.3)

hwnd = info_reader.hwnd
win32gui.ShowWindow(hwnd, 5)
win32gui.SetForegroundWindow(hwnd)
offset = (0,0)
offset = win32gui.ClientToScreen(hwnd, (0, 0))
field = Field()