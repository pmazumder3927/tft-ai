import json
import os
from collections import OrderedDict

import pandas as pd
from string_grouper import StringGrouper


class Champion:
    # static champion data for easy synergy and stat access

    print(os.listdir())
    with open("Synergies.json", "r") as file:
        synergies = json.load(open('Synergies.json'))

    with open("stats.json", "r") as file:
        stats = json.load(file)

    def __init__(self, name, star_level):
        import string_grouper
        series = pd.Series([str(name)])
        champions = pd.Series(list(self.synergies.keys()))
        similar = string_grouper.match_most_similar(champions, series)[0]
        # print(pd.DataFrame({'Input': series, 'Output': similar}).to_string)
        if similar in self.synergies:
            name = similar
            self.name = name
            self.star_level = star_level
            self.tier = self.synergies[name]["Tier"]
            self.origin = self.synergies[name]["Origin"]
            self.classes = self.synergies[name]["Classes"]
            self.position = ["", 0]
            self.items = [None] * 3
        else:
            # print("'" + name + "' is not a valid TFT champion.")
            self.name = None

    def getChampionID(self):
        if self.name:
            return list(self.synergies).index(self.name)

    def isValid(self):
        return self.name is not None

    """
    def __eq__(self, other):
        if isinstance(other, Champion):
            return self.name == other.name and self.tier == other.tier and self.items == other.items
    """

    def __str__(self):
        if self.name is None:
            return "Empty champion."
        return self.name + ": " + str(self.star_level)
