from cards import Hand

"""
Data classes relating to the game of poker
"""


class Match(object):
    """Container for information about a group of games"""
    def reset_match(self):
        self.round = 0
        self.opponents = []
        self.me = None

    def update_match(self):
        if 'yourBot' in self.sharedData:
            self.me = self.sharedData.pop('yourBot')
            if self.me in self.opponents:
                del self.opponents[self.me]

        if 'round' in self.sharedData:
            round_string = self.sharedData.pop('round')
            try:
                self.round = int(round_string)
            except ValueError:
                pass

        if 'bots' in self.sharedData:
            bot_list = self.sharedData.pop('bots')
            for bot in bot_list:
                if bot == self.me:
                    continue
                self.opponents.append(bot)


class Round(object):
    """Memory for a full hand of poker"""
    def reset_round(self):
        self.table_cards = []
        self.hand = None
        self.pot = 0
        self.sidepot = 0
        self.bets = {}
        self.big_blind = 0
        self.small_blind = 0
        self.button = None

    def update_round(self):
        self.parse_blinds()
        self.parse_cards()
        self.parse_pot()
        self.parse_bets()

        if 'onButton' in self.sharedData:
            self.button = self.sharedData.pop('onButton')

        if 'roundOver' in self.sharedData:
            round_is_over = self.sharedData.pop('roundOver')
            if round_is_over:
                self.reset_round()

    def parse_cards(self):
        if hasattr(self, 'me') and self.me:
            key = ('hand', self.me)
            if key in self.sharedData:
                cards = self.sharedData.pop(key)
                self.hand = Hand(cards[0], cards[1])

        if 'table' in self.sharedData:
            self.table_cards = self.sharedData.pop('table')

    def parse_pot(self):
        if 'pot' in self.sharedData:
            pot_str = self.sharedData.pop('pot')
            try:
                self.pot = int(pot_str)
            except ValueError:
                pass

        if 'sidepots' in self.sharedData:
            sidepot_str = self.sharedData.get("sidepots", "[0]")
            try:
                # strip []'s
                sidepot_str = sidepot_str.replace('[', '').replace(']', '')
                if sidepot_str == '':
                    self.sidepot = 0
                else:
                    self.sidepot = int(sidepot_str)
            except:
                pass

    def parse_blinds(self):
        if 'smallBlind' in self.sharedData:
            sb_string = self.sharedData.pop('smallBlind')
            try:
                self.small_blind = int(sb_string)
            except ValueError:
                pass

        if 'bigBlind' in self.sharedData:
            bb_string = self.sharedData.pop('bigBlind')
            try:
                self.big_blind = int(bb_string)
            except ValueError:
                pass

    def parse_bets(self):
        if not hasattr(self, 'opponents') or not self.opponents:
            return
        for bot in self.opponents + [self.me]:
            bet_key = ('bet', bot)
            bet = self.sharedData.get(bet_key)
            if bet:
                self.bets[bot] = bet


class GameData(Match, Round):
    """Aggregate data classes mixed in together"""
    def __init__(self, sharedData):
        self.sharedData = sharedData
        self.reset()

    def reset(self):
        self.reset_match()
        self.reset_round()

    def update(self):
        self.update_match()
        self.update_round()
