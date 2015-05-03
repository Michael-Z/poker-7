import sys

import utility; utility.fix_paths()
from theaigame_arena import TheAiGameArena


class GauntletArena(object):
    ENEMIES = [
        "agents/check_fold_bot.py",
        "agents/call_bot.py",
        "agents/raise_bot.py",
        "agents/call_raise_bot.py",
    ]
    ATTEMPTS = 100
    BOT_LOAD_DELAY_SECS = 0.1

    def __init__(self, challenger, percentage=100):
        self.challenger = challenger
        self.percentage = 100
        self.wins = {}

    def run(self):
        for enemy in self.ENEMIES:
            if enemy == self.challenger:
                continue
            print "\nplaying {}".format(enemy)
            for i in range(self.ATTEMPTS):
                winners = self.run_match(challenger, enemy)
                self.handle_winners(enemy, winners)
                sys.stdout.flush()

    def run_match(self, challenger, enemy):
        with TheAiGameArena(silent=True) as arena:
            arena.delay_secs = self.BOT_LOAD_DELAY_SECS
            arena.print_bot_output = False
            bot_list = [challenger, enemy]
            winners = arena.run(bot_list)
            return [b.state.source for b in winners]

    def handle_winners(self, enemy, winner_filenames):
        wins = self.wins.get(enemy, 0)
        if self.challenger in winner_filenames:
            wins += 1
        self.wins[enemy] = wins

    def __repr__(self):
        lines = []
        lines.append("Challenger: {}".format(self.challenger))
        for enemy, wins in iter(sorted(self.wins.items())):
            win_percentage = utility.MathUtils.percentage(wins, self.ATTEMPTS)
            grade = "PASS" if win_percentage >= self.percentage else "FAIL"
            line = "    {g}  {e:^30} - {w}/{a} ({p}%)" \
              .format(g=grade, e=enemy, w=wins, a=self.ATTEMPTS, p=win_percentage)
            lines.append(line)
        return "\n".join(lines)


if __name__ == '__main__':
    challenger = sys.argv[1]
    percentage = sys.argv[2] if len(sys.argv) > 2 else 100
    print "Starting gauntlet for '{}'".format(challenger)
    arena = GauntletArena(challenger, 100)
    arena.run()
    print "\nGauntlet results:\n {}".format(arena)
