import unittest
from pokeher.cards import *
from pokeher.game import *
from pokeher.theaigame import *

class MatchTest(unittest.TestCase):
    """Tests for the match-level (constant) info"""

    def test_load_opponents_me(self):
        """Tests finding our bot's name and our opponents names"""
        sharedData = {}
        match = GameData(sharedData)
        parser = SettingsParser(sharedData)
        lines = ['bot_0 seat 0',
                 'bot_1 seat 1',
                 'bot_4 seat 3',
                 'Settings your_bot bot_0']
        for line in lines:
            self.assertTrue(parser.handle_line(line))
        match.update()

        self.assertTrue(match, "match instantiated")
        self.assertEqual(match.me, "bot_0")
        self.assertTrue(match.opponents)
        self.assertTrue('bot_1' in match.opponents)
        self.assertTrue('bot_4' in match.opponents)
        self.assertFalse('bot_0' in match.opponents)

    def test_round(self):
        """Tests getting the current round"""
        sharedData = {}
        match = GameData(sharedData)
        parser = RoundParser(sharedData)
        self.assertEqual(match.round, 0)
        self.assertTrue(parser.handle_line('Match round 8'))
        match.update()
        self.assertEqual(match.round, 8)

        self.assertTrue(parser.handle_line('Match round 8392'))
        match.update()
        self.assertEqual(match.round, 8392)
        self.assertTrue(parser.handle_line('Match round lkfashfas'))
        self.assertEqual(match.round, 8392) # shouldn't change or explode

    def test_bad_match_values(self):
        """Checks for bad round"""
        sharedData = {'round' : 'ROUND'}
        match = GameData(sharedData)
        match.update()
        self.assertNotEqual(match.round, 'ROUND')

class RoundTest(unittest.TestCase):
    """Tests for round by round stuff - cards and bots and blinds etc"""

    def test_blinds_button(self):
        """Test getting the blind and button"""
        sharedData = {}
        the_round = GameData(sharedData)
        parser = RoundParser(sharedData)
        lines = ['Match small_blind 10',
                 'Match big_blind 20',
                 'Match on_button bot_0']

        for line in lines:
            self.assertTrue(parser.handle_line(line))
        the_round.update()

        self.assertEqual(the_round.small_blind, 10)
        self.assertEqual(the_round.big_blind, 20)
        self.assertEqual(the_round.button, 'bot_0')

    def test_bad_round_values(self):
        """Makes sure the round doesn't explode when we pass it bad data"""
        sharedData = {'small_blind' : 'SMALL',
                      'big_blind' : 'BIG',
                      'pot' : 'POT',
                      'sidepots' : 'SIDEPOTS'}
        the_round = Round()
        the_round.sharedData = sharedData
        the_round.reset_round()

        the_round.update_round()
        self.assertNotEqual(the_round.small_blind, 'SMALL')
        self.assertNotEqual(the_round.big_blind, 'BIG')
        self.assertNotEqual(the_round.pot, 'POT')
        self.assertNotEqual(the_round.sidepot, 'SIDEPOTS')

    def test_cards(self):
        """Tests finding the cards"""
        sharedData = {}
        data = GameData(sharedData)
        data.me = 'bot_0'
        callback = None
        parser = TurnParser(sharedData, callback)
        lines = ['bot_0 hand [6c,Jc]',
                 'Match max_win_pot 20',
                 'Match table [Tc,8d,9c]',
                 'Match sidepots [10]']

        for line in lines:
            self.assertTrue(parser.handle_line(line))
        data.update()

        self.assertEqual(data.hand,
                         Hand(Card(6, C.CLUBS), Card(C.JACK, C.CLUBS)))
        self.assertEqual(data.table_cards, [Card(10, C.CLUBS), Card(8, C.DIAMONDS), Card(9, C.CLUBS)])
        self.assertEqual(data.pot, 20)
        self.assertEqual(data.sidepot, 10)

        parser.handle_line('Match sidepots []')
        data.update()
        self.assertEqual(data.sidepot, 0)

        parser.handle_line('bot_0 wins 90')
        data.update()
        self.assertFalse(data.hand)
        self.assertEqual(data.pot, 0)

    def test_bets(self):
        sharedData = {}
        data = GameData(sharedData)
        data.me = 'bot_0'
        callback = None
        parser = TurnParser(sharedData, callback)
        lines = [
            "Match on_button bot_0",
            "Match small_blind 10",
            "Match big_blind 20",
            "bot_0 stack 3920",
            "bot_1 stack 1000",
            "bot_0 post 10",
            "bot_1 post 20",
            "bot_1 hand [8c,Ts]",
            "bot_0 hand [Qc,9d]",
            "Match max_win_pot 30",
            "Match sidepots [20]",
        ]

        for line in lines:
            self.assertTrue(parser.handle_line(line))
            data.update()

        # Did we pick up the blinds correctly?
        print "{}".format(data.bets)
        self.assertEqual(data.bets["bot_0"], 10)
        self.assertEqual(data.bets["bot_1"], 20)

        more_bets = [
            'bot_0 raise 40',
            'bot_1 call 40',
        ]

        for line in more_bets:
            self.assertTrue(parser.handle_line(line))
        data.update()

        # and more bets
        self.assertEqual(data.bets["bot_0"], 50)
        self.assertEqual(data.bets["bot_1"], 60)

        self.assertTrue(parser.handle_line("Match sidepots [0]"))
        data.update()

        self.assertEqual(data.bets["bot_0"], 0)
        self.assertEqual(data.bets["bot_1"], 0)

if __name__ == '__main__':
    unittest.main()
