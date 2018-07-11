
from threading import Lock
lock = Lock()

class Guessing:

    language_data = None
    chosen_word_list = None

    def __init__( self, language_data, chosen_word_list ):
        self.language_data = language_data
        self.chosen_word_list = chosen_word_list

    def _evaluation(self, level, player_guess):
        lock.acquire()
        # print("Lock acquired!")
        state = False
        adjustment_rate = 0.0

        try:
             # only one thread can execute code there
            correct_letter = self.chosen_word_list[level]
            correct_index = self.language_data.index( correct_letter )
            player_guess_index = self.language_data.index( player_guess )

            if (correct_letter == player_guess):
                level = level + 1
                state = True
            else:
                language_data_count = len(self.language_data)
                index_difference = abs(correct_index - player_guess_index)
                percentage_ratio_per_char = round( (100/language_data_count), 2)
                adjustment_rate = round( (index_difference*percentage_ratio_per_char), 2)
        finally:
            lock.release() #release lock
            # print("Lock released!")
    
            return {
                'level': level,
                'state': state,
                'adjustment_rate': adjustment_rate
            }
