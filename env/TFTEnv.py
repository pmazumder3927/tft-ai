import random
import json
import gym
import pyautogui
import win32gui
from PIL import ImageGrab
from gym import spaces
import pandas as pd
import numpy as np
import math

from Field import Field
from PlayerControl import PlayerControl
from ScreenInterpreter import ScreenInterpreter

MAX_ACCOUNT_BALANCE = 2147483647
MAX_NUM_SHARES = 2147483647
MAX_SHARE_PRICE = 5000
MAX_OPEN_POSITIONS = 5
MAX_STEPS = 20000

INITIAL_ACCOUNT_BALANCE = 10000


class TFTEnv(gym.Env):
    """A stock trading environment for OpenAI gym"""
    metadata = {'render.modes': ['human']}

    def __init__(self):
        super(TFTEnv, self).__init__()
        self.reward_range = (0, MAX_ACCOUNT_BALANCE)

        # Actions of the format Buy x%, Sell x%, Hold, etc.
        self.action_space = spaces.Box(
            low=np.array([0, 0]), high=np.array([8, 1]), dtype=np.float16)

        """
        Multidiscrete action space as follows:
        1. Buy Champion: Discrete 6 - NOOP[0], BUY[1-5]
        2. Sell Champion: Discrete 6 (from bench) - NOOP[0], SELL[1-9]
        3. Level up: Discrete 2 - NOOP[0], LEVEL[1]
        4. Reroll: Discrete 2 - NOOP[0], REROLL[2]
        5. Move Champion from board to bench: Discrete 190 - NOOP[0], MOVE[1-189]
        6: Move Champion from bench to board: Discrete 190 - NOOP[0], MOVE[1-189]
        8. Move Champion from board to board: Discrete 421 - NOOP[0], MOVE[1-420]
        """
        self.action_space = spaces.MultiDiscrete([5, 10, 421, 2, 2])
        # Prices contains the OHCL values for the last five prices
        """
        Observation space:
        Bench: [9, 5]
        Board: [21, 5]
        Store: [5, 5] [Slot 1-5][Champion ID, Stars, Tier, Synergy 1, Synergy 2]
        """
        self.observation_space = spaces.Box(0, 5, shape=(35, 6), dtype=np.int)
        # main execution
        self.info_reader = ScreenInterpreter()
        self.pc = PlayerControl()
        self.field = Field()
        self.offset = win32gui.ClientToScreen(self.info_reader.hwnd, (0, 0))
        self.pc.setOffset(self.offset)
        self.current_step = 0

    def testStoreVision(self):
        "Reads champions in store from screenshot, adds them to board, then prints synergies."
        print("Reading...")
        self.info_reader.readStore()
        print("Identified champs from store: " + str(self.info_reader.getStore()))
        print("Identified gold total: " + str(self.info_reader.getGold()))

    def testManeuvering(self):
        "Tests moving champions around."
        print("Maneuvering...")
        pc = self.pc
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

    def scanBench(self):
        field = self.field
        offset = self.offset
        for i in range(9):
            pyautogui.mouseDown(button='right', x=960 + offset[0], y=300 + offset[1])
            pyautogui.mouseUp(button='right')
            pos = (420 + 122 * i, 775)
            pyautogui.mouseDown(button='right', x=pos[0] + offset[0], y=pos[1] + offset[1])
            pyautogui.mouseUp(button='right')
            champion = self.info_reader.readChampion(pos[0] + offset[0], pos[1] + offset[1] - 120, pos[0] + offset[0] + 400,
                                                pos[1] + offset[1] + 150)
            field.addChampionToBench(champion, i)
        print(field.getBoardRepresentation())
        print(field.getBenchRepresentation())
        print(field)
        field.parseShop(self.info_reader.getStore())
        print(field.shop)

    def _next_observation(self):
        """
        # Get the stock data points for the last 5 days and scale to between 0-1
        frame = np.array([
            self.df.loc[self.current_step: self.current_step +
                        5, 'Open'].values / MAX_SHARE_PRICE,
            self.df.loc[self.current_step: self.current_step +
                        5, 'High'].values / MAX_SHARE_PRICE,
            self.df.loc[self.current_step: self.current_step +
                        5, 'Low'].values / MAX_SHARE_PRICE,
            self.df.loc[self.current_step: self.current_step +
                        5, 'Close'].values / MAX_SHARE_PRICE,
            self.df.loc[self.current_step: self.current_step +
                        5, 'Volume'].values / MAX_NUM_SHARES,
        ])

        # Append additional data and scale each value to between 0-1
        """
        self.scanBench()
        print(self.field.board.shape)
        print(self.field.bench.shape)
        print(self.field.shop.shape)

        obs = np.concatenate((self.field.board, self.field.bench, self.field.shop), axis=0)
        print(obs.shape)
        return obs

    def _take_action(self, action):
        buyChampion = action[0]
        sellChampion = action[1]
        levelUp = action[2]
        reroll = action[3]
        moveChampion = action[4]
        if buyChampion != 0:
            # Buy Champion
            self.pc.buyChampion(buyChampion)
            self.field.addChampionToBench(self.field.shop_position[buyChampion])
        if sellChampion != 0:
            # Sell Champion
            self.pc.sellChampion(sellChampion)
        if levelUp != 0:
            self.pc.levelUp()
        if moveChampion != 0:
            n = 220
            p1 = int(n / 21)
            p2 = n % 21
            p2 = p2 + int(math.ceil(n / 21.0)) - 1
            if p2 > 20:
                p1 = p1 + 1
                p2 = p2 - 21
            self.pc.reorderChampOnBoard(p1, p2)
        if reroll != 0:
            self.pc.reroll()

    def step(self, action):
        # Execute one time step within the environment
        self._take_action(action)

        self.current_step += 1

        delay_modifier = (self.current_step / MAX_STEPS)

        reward = self.field.calculateSynergyReward() * delay_modifier
        done = False

        obs = self._next_observation()

        return obs, reward, done, {}

    def reset(self):
        # Reset the state of the environment to an initial state
        return self._next_observation()

    def render(self, mode='human', close=False):
        return
        # Render the environment to the screen