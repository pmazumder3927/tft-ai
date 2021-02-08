from Champion import Champion
import numpy as np


class Field:
    def __init__(self):
        self.champions = {}
        self.board_position = [None] * 21
        self.board = np.zeros(shape=(21, 6))
        self.bench = np.zeros(shape=(9, 6))
        self.shop = np.zeros(shape=(5,6))
        self.board_capacity = 1
        self.bench_position = [None] * 9
        self.shop_position = [None] * 5
        self.active_synergies = {
            "Blademaster": {"active": 0, "required": [3, 6, 9], "ID": 0},
            "Blaster": {"active": 0, "required": [2, 4], "ID": 1},
            "Brawler": {"active": 0, "required": [2, 4], "ID": 2},
            "Demolitionist": {"active": 0, "required": [2], "ID": 3},
            "Infiltrator": {"active": 0, "required": [2, 4], "ID": 4},
            "Mana-Reaver": {"active": 0, "required": [2], "ID": 5},
            "Mercenary": {"active": 0, "required": [1], "ID": 6},
            "Mystic": {"active": 0, "required": [2, 4], "ID": 7},
            "Paragon": {"active": 0, "required": [1], "ID": 8},
            "Protector": {"active": 0, "required": [2, 4, 6], "ID": 9},
            "Sniper": {"active": 0, "required": [2, 4], "ID": 10},
            "Sorcerer": {"active": 0, "required": [2, 4, 6], "ID": 11},
            "Starship": {"active": 0, "required": [1], "ID": 0},
            "Vanguard": {"active": 0, "required": [2, 4, 6], "ID": 12},
            "Astro": {"active": 0, "required": [3], "ID": 13},
            "Battlecast": {"active": 0, "required": [2, 4, 6, 8], "ID": 14},
            "Celestial": {"active": 0, "required": [2, 4, 6], "ID": 15},
            "Chrono": {"active": 0, "required": [2, 4, 6, 8], "ID": 16},
            "Cybernetic": {"active": 0, "required": [3, 6], "ID": 17},
            "Dark Star": {"active": 0, "required": [2, 4, 6, 8], "ID": 18},
            "Mech-Pilot": {"active": 0, "required": [3], "ID": 19},
            "Rebel": {"active": 0, "required": [3, 6, 9], "ID": 20},
            "Space Pirate": {"active": 0, "required": [2, 4], "ID": 21},
            "Star Guardian": {"active": 0, "required": [3, 6, 9], "ID": 22},
        }

    def addChampionToBoard(self, champion, pos_idx):
        """
        Adds champion to internal board representation and updates synergies. Duplicate champions will not proc additional synergies.
        """
        if not champion:
            return
        self.board_position[pos_idx] = champion
        champion.position = ["board", pos_idx]
        if not champion.name in self.champions:
            for champ_origin in champion.origin:
                self.active_synergies[champ_origin]["active"] += 1
            for champ_class in champion.classes:
                self.active_synergies[champ_class]["active"] += 1
            self.champions[champion.name] = {champion.star_level: [champion]}
        else:
            if not champion.star_level in self.champions[champion.name]:
                self.champions[champion.name][champion.star_level] = [champion]
            else:
                self.champions[champion.name][champion.star_level].append(champion)

    def removeChampionFromBoard(self, champion):
        """
        Removes champion from internal board representation and updates synergies. Removing duplicate will not change synergies.
        """
        if not champion:
            return
        for idx, champ in enumerate(self.board_position):
            if champ == champion:
                self.board_position[idx] = None
        if champion.name in self.champions:
            if len(self.champions[champion.name]) == 1:
                for champ_origin in champion.origin:
                    self.active_synergies[champ_origin]["active"] -= 1
                for champ_class in champion.classes:
                    self.active_synergies[champ_class]["active"] -= 1
                self.champions.pop(champion.name)
            else:
                if len(self.champions[champion.name][champion.star_level]) == 1:
                    self.champions[champion.name].pop(champion.star_level)
                else:
                    self.champions[champion.name][champion.star_level].remove(champion)

    def addChampionToBench(self, champion, idx = -1):
        """
        Adds champion to internal bench representation at first open slot.
        """
        if not champion:
            return
        if not champion.isValid():
            return
        if not idx == -1:
            self.bench_position[idx] = champion
            return

        for pos_idx, pos in enumerate(self.bench_position):
            if pos is None:
                self.bench_position[pos_idx] = champion
                champion.position = ["bench", pos_idx]
                if not champion.name in self.champions:
                    self.champions[champion.name] = {champion.star_level: [champion]}
                else:
                    if not champion.star_level in self.champions[champion.name]:
                        self.champions[champion.name][champion.star_level] = [champion]
                    else:
                        self.champions[champion.name][champion.star_level].append(
                            champion
                        )
                        if (
                                len(self.champions[champion.name][champion.star_level]) == 3
                                and champion.star_level > 0
                                and champion.star_level < 3
                        ):
                            print("3 champions of star level " + str(champion.star_level) + " found.")
                            # change to different star
                            upgraded_champ = Champion(
                                champion.name, champion.star_level + 1
                            )
                            prev_position = self.champions[champion.name][
                                champion.star_level
                            ][0].position
                            for champ in self.champions[champion.name][
                                champion.star_level
                            ].copy():
                                if champ.position[0] == "board":
                                    self.removeChampionFromBoard(champ)
                                else:
                                    self.removeChampionFromBench(champ)
                            if prev_position[0] == "board":
                                self.addChampionToBoard(upgraded_champ, prev_position[1])
                            else:
                                self.addChampionToBench(upgraded_champ)
                break

    def removeChampionFromBench(self, champion):
        """
        Removes champion from internal bench representation, prioritizing first.
        """
        if not champion:
            return
        for idx, champ in enumerate(self.bench_position):
            if champ == champion:
                self.bench_position[idx] = None
        if champion.name in self.champions:
            if len(self.champions[champion.name]) == 1:
                self.champions.pop(champion.name)
            else:
                if len(self.champions[champion.name][champion.star_level]) == 1:
                    self.champions[champion.name].pop(champion.star_level)
                else:
                    self.champions[champion.name][champion.star_level].remove(champion)

    def hasEmptySpaces(self):
        """
        To do: returns whether the field has an empty bench slot.
        """
        for champ in self.bench_position:
            if champ is None:
                return True
        return False

    def calculateSynergyReward(self):
        reward = 0
        for i in self.active_synergies:
            for j, k in enumerate(self.active_synergies[i]['required']):
                if self.active_synergies[i]['active'] >= k:
                    reward += (j + 1) * 2
        return reward

    def getBoardRepresentation(self):
        for i, champion in enumerate(self.board_position):
            if champion:
                self.board[i] = self.serializeChampion(champion)
        return self.board

    def getBenchRepresentation(self):
        for i, champion in enumerate(self.bench_position):
            if champion:
                self.bench[i] = self.serializeChampion(champion)
        return self.bench

    def parseShop(self, shop):
        for ind, name in enumerate(shop):
            champion = Champion(name, 1)
            if champion.isValid():
                self.shop_position[ind] = champion
                self.shop[ind] = self.serializeChampion(champion)

    def serializeChampion(self, champion):
        num_classes = len(champion.classes)
        if num_classes < 2:
            return [champion.getChampionID(),
                             champion.star_level,
                             champion.tier,
                             self.active_synergies[champion.origin[0]]['ID'],
                             self.active_synergies[champion.classes[0]]['ID'],
                             0]
        else:
            return [champion.getChampionID(),
                             champion.star_level,
                             champion.tier,
                             self.active_synergies[champion.origin[0]]['ID'],
                             self.active_synergies[champion.classes[0]]['ID'],
                             self.active_synergies[champion.classes[1]]['ID']]
            return

    def __str__(self):
        return (
                "Bench: "
                + str(list(map(str, self.bench_position)))
                + "\nBoard: "
                + str(list(map(str, self.board_position)))
        )
