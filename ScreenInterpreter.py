import cv2
import win32gui
from PIL import Image, ImageGrab
import PIL.ImageOps
import pytesseract
import re
import numpy as np
from matplotlib import pyplot as plt

from Champion import Champion


class ScreenInterpreter:

    # constructor
    def __init__(self):
        pytesseract.pytesseract.tesseract_cmd = 'D:\\Program Files\\Tesseract-OCR\\tesseract.exe'
        # track relevant data on the frame
        self.data = {
            "board": [],
            "store": [None] * 5,
            "gold": 0,
            "level": 0,
            "xp": 0,
            "win_streak": 0,
            "items": {
                "chain_vest": 0,
                "negatron_cloak": 0,
                "needlessly_large_rod": 0,
                "bf_sword": 0,
                "recurve_bow": 0,
                "golden_spatula": 0,
            },
        }
        self.hwnd = self.getHWND()

    def getHWND(self):
        toplist, winlist = [], []

        def enum_cb(hwnd, results):
            winlist.append((hwnd, win32gui.GetWindowText(hwnd)))

        win32gui.EnumWindows(enum_cb, toplist)

        firefox = [(hwnd, title) for hwnd, title in winlist if 'client' in title.lower()]
        # just grab the hwnd for first window matching firefox
        if firefox:
            firefox = firefox[0]
            self.hwnd = firefox[0]
        else:
            self.hwnd = winlist[0]
            print('window not found')
        return self.hwnd

    # main function: reads data from in-game screenshot
    def retrieveData(self, screenshot):
        """
        Retrieves relevant data (e.g. champs, gold, items, etc.) from the latest screenshot.
        """
        # run tesseract to locate text
        # recognize champs in store and on board
        # see gold
        # if champ info open, record

        # update store
        x = 485
        for i in range(5):
            self.data["store"][i] = self.read(
                self.cropAndEdit(screenshot, x, 1041, x + 140, 1069)
            )
            x += 201

        # update gold
        thresh = 150
        fn = lambda x: 255 if x > thresh else 0
        gold = (
            self.cropAndEdit(screenshot, 873, 881, 906, 910)
            .resize((200, 200), Image.ANTIALIAS)
            .convert("L")
            .point(fn, mode="1")
        )
        str_gold = self.read(gold, whitelist="0123456789").strip()
        if len(str_gold) < 1:
            str_gold = pytesseract.image_to_string(gold,
                            config="--psm 10 -c tessedit_char_whitelist=0123456789").strip()

        if str_gold.isnumeric():
            self.data["gold"] = int(str_gold)

        round_num = (
            self.cropAndEdit(screenshot, 743, 9, 819, 32)
            .resize((200, 200), Image.ANTIALIAS)
            .convert("L")
            .point(fn, mode="1")
        )
        
        str_round = self.read(round_num, whitelist="0123456789-").strip()

    def cropAndEdit(self, img, x1, y1, x2, y2):
        """
        Crops, inverts, and desaturates image.
        """
        img1 = PIL.ImageOps.invert(img.crop((x1, y1, x2, y2)))
        img1 = img1.convert("L")
        img1.save("out.png")
        return img1

    def read(self, img, blacklist=".,", whitelist=None):
        """
        Performs the tesseract operation on a cropped image after inversion and desaturation.
        """
        if whitelist:
            return pytesseract.image_to_string(
                img, config="-c tessedit_char_whitelist=" + whitelist
            )
        else:
            return pytesseract.image_to_string(
                img, config="-c tessedit_char_blacklist=" + blacklist
            )

    def readStore(self):
        pos = win32gui.GetClientRect(self.hwnd)
        it = iter(pos)
        pos = list(zip(it, it))
        bbox = win32gui.ClientToScreen(self.hwnd, pos[0]) + win32gui.ClientToScreen(self.hwnd, pos[1])
        img = ImageGrab.grab(bbox)
        self.retrieveData(img)

    def getStore(self):
        """
        Returns array containing champions found in store (use after retrieval).
        """
        return self.data["store"]

    def getGold(self):
        """
        Returns current gold count (use after retrieval).
        """
        return self.data["gold"]

    def readChampion(self, x, y, x2, y2):
        img = ImageGrab.grab((x, y, x2, y2))
        img.save('champiton.png')
        img = np.array(img)
        template = cv2.imread('feature.PNG')
        res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        template2 = cv2.imread('feature2star.PNG')
        res2 = cv2.matchTemplate(img, template2, cv2.TM_CCOEFF_NORMED)
        min_val2, max_val2, min_loc2, max_loc2 = cv2.minMaxLoc(res2)

        """
        print(max_val)
        print(min_val)
        print("-------")
        print(max_val2)
        print(min_val2)
        print('============')
        """
        """
        if max_val2 > max_val:
            max_loc = max_loc2
            template = template2
            """
        top_left = max_loc
        bottom_right = (top_left[0] + template.shape[1], top_left[1] + template.shape[0])

        thresh = 100
        fn = lambda x: 255 if x > thresh else 0
        text = (
            self.cropAndEdit(Image.fromarray(img), max_loc[0]+100, max_loc[1] + 87, max_loc[0] + template.shape[1], max_loc[1] + template.shape[0] - 73)
            .convert("L")
            .point(fn, mode="1")
        )

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        text = np.array(text)
        text.dtype = 'uint8'
        print(text.dtype)
        text = cv2.morphologyEx(text, cv2.MORPH_OPEN, kernel)

        red = pytesseract.image_to_string(text, config="--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz").strip()

        champion = Champion(red, 1)
        cv2.rectangle(img, top_left, bottom_right, 255, 2)
        plt.subplot(131), plt.imshow(res, cmap='gray')
        plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
        plt.subplot(132), plt.imshow(img, cmap='gray')
        plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
        plt.subplot(133), plt.imshow(text, cmap='gray')
        plt.title('Detected Text: ' + red)
        plt.show()
        return champion
        """
        print(
            pytesseract.image_to_string(img,
                            config="--psm 6 -c tessedit_char_blacklist=., #"))"""