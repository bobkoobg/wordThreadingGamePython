import json, os, _thread, json, collections, sys,time, datetime

from random import randint

script_dir = os.path.dirname(os.path.realpath(__file__))
words_file = open('{0}/libs/words.json'.format(script_dir), 'r')
words_data = json.load(words_file)
gen_names = words_data['gen_names']

rand_phrase = randint( 0, len(words_data['w'])-1 )

chosen_word = words_data['w'][rand_phrase]
chosen_word_list = list( words_data['w'][rand_phrase] )
chosen_word_list_count = len(chosen_word_list)

language_file = open('{0}/libs/language.json'.format(script_dir), 'r')
language_data = json.load(language_file)['a']

startup_time = datetime.datetime.now()
startup_time_str = startup_time.strftime("%d/%m/%Y %H:%M:%S")

from libs import player_alpha
from libs.guessing_evaluation import Guessing
from libs.player_alpha import Player
from concurrent.futures import ThreadPoolExecutor

guess_obj = Guessing( language_data, chosen_word_list )

def printer( finished_participants, new_next_generation, options ):
    curr_time_elapsed = ( datetime.datetime.now() - startup_time )
    curr_time_elapsed_secs = curr_time_elapsed.seconds

    if( options['winning_time'] ):
        curr_time_elapsed = ( options['winning_time'] - startup_time )
        curr_time_elapsed_secs = curr_time_elapsed.seconds

    print("\n###\tSentence:'{0}'".format(chosen_word))
    print("###\tStartup time:'{0}'".format(startup_time_str))

    if( options['termination'] ):
        print("###\tEnd time: '{0}'".format( datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") ))

    print("###\tTotal levels: {0}".format(chosen_word_list_count))
    print("###\tRound #{0}".format(options['round_index']))
    if( options['winning_index'] is not -1 ):
        print("\n###\tWinner Winner Chicken Dinner! => {0}\n".format( finished_participants[0]['name'] ))

    print("#Rank;\tName;\t\tLevel;\tSuccess%;\tLeading quota%;\tElapsed[%M:%S];\tRounds latency;\tResult;")

    for fp_idx,fp_res in enumerate(finished_participants):

        print("[{0}]\t{1}\t{2}\t{3}%\t\t{4}%\t\t{5}\t\t{6}\t\t'{7}'".format(
            fp_res['rank'],
            fp_res['name'],
            fp_res['level'],
            '100.00',
            fp_res['leading_percent'],
            fp_res['time'],
            fp_res['rounds_behind'],
            fp_res['known']
        ))

    for nng_idx,nng_res in enumerate(new_next_generation):
        time = (datetime.datetime.now() - startup_time ) if options['winning_time'] == None else ( datetime.datetime.now() - options['winning_time'] )
        time_structured = ( "+" if options['winning_time'] is not None else "" ) + datetime.datetime.strptime( str(time), '%H:%M:%S.%f').strftime('%M:%S')
        rounds_behind = ( "+" if options['winning_index'] is not -1 else "" ) + str( round( (options['round_index']/options['winning_index']) , 2) if options['winning_index'] is not -1 else 0.0)

        print("[{0}]\t{1}\t{2}\t{3}%\t\t{4}%\t\t{5}\t\t{6}\t\t'{7}'".format(
            nng_res['rank'],
            nng_res['name'],
            nng_res['level'],
            round( (100/chosen_word_list_count)*nng_res['level'] , 2),
            round( (100/ options['round_index'] )*nng_res['leading'] , 2) if options['winning_index'] == -1 else round( (100/options['winning_index'])*nng_res['leading'] , 2),
            time_structured,#"+{0} seconds".format(curr_time_elapsed_secs) if options['winning_time'] != None else curr_time_elapsed,
            rounds_behind,
            nng_res['known']
        ))

def player_init( name, level, language_data, guess_obj, history, known, leading ):
    player = Player( name, level, language_data, guess_obj, history, known, leading )
    return player.get()

def logic( finished_participants, next_generation, options ):

    round_index = options['round_index']
    winning_index = options['winning_index']
    winning_time = options['winning_time']

    executor = ThreadPoolExecutor(max_workers= len(next_generation) )
    futures = []
    for ng_item in next_generation:
        futures.append(
            executor.submit(
                player_init, #thats the function and all others are params to it
                ng_item['name'],
                ng_item['level'],
                language_data,
                guess_obj,
                ng_item['history'],
                ng_item['known'],
                ng_item['leading']
            )
        )

    results = []
    for future in futures:
        result = future.result()
        results.append( result )

    results.sort(key=lambda x: x['adjustment_rate'], reverse=False)
    results.sort(key=lambda x: x['state'], reverse=True)
    results.sort(key=lambda x: x['leading'], reverse=True)
    results.sort(key=lambda x: x['level'], reverse=True)

    new_next_generation = [];

    max_level = 0
    curr_rank = len(finished_participants) + 1
    curr_rank_level = 0
    for index,result in enumerate(results):
        
        if( index == 0):
            max_level = result['level']
            curr_rank_level = result['level']
        elif( curr_rank_level != result['level'] ):
            curr_rank = index+1
            curr_rank_level = result['level']

        new_next_generation.append({
            'rank': curr_rank,
            'name': result['name'],
            'level': result['level'],
            'history': result['history'],
            'known': result['known'],
            'leading' : result['leading']+1 if max_level == result['level'] and winning_index is -1 else result['leading']
        })

    printer( finished_participants, new_next_generation, {
        'round_index': round_index,
        'winning_index' : winning_index,
        'winning_time': winning_time,
        'termination': False
    })

    time.sleep( 0.1 )
    print("... next ...")
    return new_next_generation


def game( next_generation ):
    round_index = 0
    winning_index = -1
    winning_time = None
    finished_participants = []

    while True:
        finished_indexes_this_round = []
        round_index = round_index + 1
        new_generation = logic(finished_participants, next_generation, {
            'round_index': round_index,
            'winning_index' : winning_index,
            'winning_time' : winning_time
        })

        for ng_val in new_generation:
            if( ng_val['known'] == chosen_word ):

                time = (datetime.datetime.now() - startup_time ) if winning_time == None else ( datetime.datetime.now() - winning_time )
                time_structured = ( "+" if winning_time is not None else "" ) + datetime.datetime.strptime( str(time), '%H:%M:%S.%f').strftime('%M:%S')
                rounds_behind = ( "+" if winning_index is not -1 else "" ) + str(  round( (round_index/winning_index) , 2) if winning_index is not -1 else 1.0)

                if( winning_index == -1 ):
                    winning_index = round_index
                    winning_time = datetime.datetime.now()

                finished_participants.append({
                    'rank': ng_val['rank'],
                    'name': ng_val['name'],
                    'level': ng_val['level'],
                    'history': ng_val['history'],
                    'known': ng_val['known'],
                    'leading' : ng_val['leading'],
                    'leading_percent' : round( (100/round_index)*ng_val['leading'] , 2) if winning_index == -1 else round( (100/winning_index)*ng_val['leading'] , 2),
                    'rounds_behind' : rounds_behind,
                    'time' : time_structured
                })
                finished_indexes_this_round.append( new_generation.index( ng_val ) )

        finished_indexes_this_round.reverse()
        for f_idx in finished_indexes_this_round:
            new_generation.pop(f_idx)

        if not new_generation:
            printer( finished_participants, new_generation, {
                'round_index': round_index,
                'winning_index' : winning_index,
                'winning_time' : winning_time,
                'termination': True
            })
            sys.exit(0)

        next_generation = new_generation

def main():
    next_generation = []
    for value in gen_names:
        next_generation.append({
            'name': "Family_{0}".format(value),
            'level': 0,
            'history': [],
            'known': "",
            'leading': 0
        })
    game( next_generation )

main()
