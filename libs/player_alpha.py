import time, json

from random import randint

class Player:
    name = None
    level = None
    language_data = None
    guess_obj = None
    history = None
    known = None

    def __init__( self, name, level, language_data, guess_obj, history, known, leading ):
        # print( "Initialized '%s' at '%s'" % ( name, time.ctime( time.time() ) ) )
        self.name = name
        self.level = level
        self.language_data = language_data
        self.guess_obj = guess_obj
        self.history = history
        self.known = known
        self.leading = leading

    def get( self ):
        choice = randint( 0, len( self.language_data )-1 )

        final_state = self.guess_obj._evaluation( self.level, self.language_data[choice] )
        final_state['name'] = self.name
        final_state['history'] = self.history
        if final_state['state']:
            self.known = self.known + self.language_data[choice]
        final_state['known'] = self.known
        final_state['leading'] = self.leading

        return final_state
