#################################################
#Project: Short-term memory test for nootropics #
#Author: Lander Bodyn                           #
#Date: February 2017                            #
#Email: bodyn.lander@gmail.com                  #
#################################################

import time
import csv
from random import shuffle
import pickle

def get_symbols():
    """Read in the data of symbols, grades, meanings and readings. Symbols 
    taken from https://en.wikipedia.org/wiki/List_of_j%C5%8Dy%C5%8D_kanji"""

    with open('Japanese symbols.csv') as f:
        symbols_table = list(csv.reader(f))[1:]

    _, symbols, _, _, _, grades, _, meanings, readings = zip(*symbols_table)

    assert len(symbols) == len(grades) == len(meanings) == len(readings)

    return symbols, grades, meanings, readings

def ask_question(question, answers=None):
    """ Loop that repeats the question until one of the possible answers is
    returned. If answers is not given, it must be an integer. Could be written
    bit simpeler most likely"""

    if answers is not None:
        question += ' (' + '/'.join(answers) + '): '
        nan_str = ("{} is not one of the possible answers. Answer with '" +
            "' or '".join(answers) + "': ")
        answer = input(question)
        while answer not in answers:
            print(nan_str.format(answer))
            answer = input(question)
    else:
        question += ' '
        answer = input(question)
        while not answer.isdigit() or int(answer) < 1:
            print("Answer must be a positive integer")
            answer = input(question)
        answer = int(answer)

    return answer

def ask_settings():

    repeats = ask_question('Prevent repeating symbols from previous sessions?',
            answers='yn')

    question = ('What difficulty of symbols do you want?\nFirst grade, second grade or both?')
    difficulty = ask_question(question, answers='fsb')

    n_symbols = ask_question('How many symbols should the quiz contain?')

    n_study_time = ask_question('How many seconds to study each symbol?')

    return repeats, difficulty, n_symbols, n_study_time

def get_indices(repeats, difficulty, n_symbols):
    """ Get a shuffled list of the indices of symbols that will be used for 
    the quiz."""

    # Load indices of earlier used symbols, this object is a set
    try:
        with open('previous_indices.pkl', 'rb') as f:
            used_indices = pickle.load(f)
    except FileNotFoundError:
        print('No previous sessions found, starting fresh...')
        used_indices = set()

    # Select all indices that may be used
    all_indices = set(range(len(symbols)))
    if repeats == 'n':
        indices = all_indices - used_indices
    else:
        indices = all_indices
    indices = list(indices)

    # Select grade
    if difficulty != 'b':
        if difficulty == 'f':
            indices = [index for index in indices if grades[index] != 'S']
        else: # difficulty == 's'
            indices = [index for index in indices if grades[index] == 'S']

    # Select number of random symbols
    shuffle(indices)
    selected_indices = indices[:n_symbols]

    # Store all used indices as a set
    with open('previous_indices.pkl', 'wb') as f:
        pickle.dump(used_indices | set(selected_indices), f)

    return selected_indices

def study_symbol(index):
    """ Show the symbol of the index with pronunciation and meaning"""

    out_str = '\rSymbol: {} | pronunciation: {} | meaning: {}'
    reading = readings[index]
    roman_reading = ''.join(char for char in reading if ord(char) < 128)
    read = roman_reading.strip(' ').strip('-').split(',')
    pronunciation = ', '.join(r.strip() for i, r in enumerate(read) if i < 3)
    symbol = symbols[index]
    print('\r' + ' '*79, end = '')
    print(out_str.format(symbol, pronunciation, meanings[index]), end = '')

def test_symbol(index):
    answered_meaning = input('Meaning of symbol {}: '.format(symbols[index]))
    return int(answered_meaning == meanings[index])

def main():

    print('Settings for the quiz...')
    repeats, difficulty, n_symbols, n_study_time = ask_settings()

    selected_indices = get_indices(repeats, difficulty, n_symbols)

    print("\nEach symbol will be shown for {} seconds.".format(n_study_time))
    input("Press enter to start the study phase.")
    print()
    for index in selected_indices:
        study_symbol(index)
        time.sleep(n_study_time)
    print('\r' + ' '*79, end = '')

    # Test symbols in different order
    shuffle(selected_indices)
    score = 0
    print('\rStudy time over! Time to test...')
    for index in selected_indices:
        score += test_symbol(index)

    print('\nQuiz finished... Scored {}/{} for the quiz!'.format(score, 
        n_symbols))

if __name__ == '__main__':

    # Define these as globals to prevent a lot of function arguments
    symbols, grades, meanings, readings = get_symbols()

    main()
