from __future__ import print_function
import cPickle as pickle
import utility


class PreflopEquity(object):
    """Mapping of Hand.simple() -> win % for preflop two card hands"""
    def __init__(self, data_file='preflop_wins_50000.pickle', log_func=None):
        if log_func is None:
            log_func = self.print_log
        self.data = {}
        infile = utility.get_data_file(data_file)
        try:
            in_stream = open(infile, 'r')
            try:
                self.data = pickle.load(in_stream)
                log_func("Loaded preflop equity file")
            finally:
                in_stream.close()
        except IOError as e:
            log_func("IO error loading {f} (e={e})".format(f=infile, e=e))

    @staticmethod
    def print_log(what):
        print(what)
