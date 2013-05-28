# -*- coding: utf-8 -*-
'''
Created on May 27, 2013

@author: bryce
'''
import sys
import random
import Main

def process_file(file_name, markov_order, bigram_counts):
    '''Stores the word occurrence data from a file in the global dictionary bigram_counts.
    
    Arguments:
    file_name     -- the path to the file to read
    markov_order  -- the markov order (ex: if markov_order = 2, each generated word is based on the two previous words)
    bigram_counts -- maps tuples of words maps of the words that are preceded by the tuples in the training docs.
                     Each map matches the following-word with the number of times it occurs as a following word
    '''
    with open(file_name,'r') as text:
        for line in text:
            line_chunks = line.split()
            if line_chunks != []:
                for _ in range(markov_order):
                    line_chunks.insert(0,'@@pad@@')
                line_chunks.append('@@pad@@')
                update_bigram_counts(line_chunks, markov_order, bigram_counts)


def update_bigram_counts(line_chunks, markov_order, bigram_counts):
    '''Record the occurrence of following_word after word in a global dictionary bigram_counts.

    Arguments:
    line_chunks   -- a line of training data that has been split around whitespace and appropriately padded
    markov_order  -- the markov order (ex: if markov_order = 2, each generated word is based on the two previous words)
    bigram_counts -- maps tuples of words maps of the words that are preceded by the tuples in the training docs.
                     Each map matches the following-word with the number of times it occurs as a following word
    '''
    for i in range(markov_order, len(line_chunks)):
        preceding_words = tuple(line_chunks[i-markov_order:i])
        if bigram_counts.has_key(preceding_words):
            word_count_map = bigram_counts[preceding_words]
            count = word_count_map.get(line_chunks[i],0)
            word_count_map[line_chunks[i]] = count+1
        else:
            bigram_counts[preceding_words] = {line_chunks[i]: 1}


def produce_text(probabilities, markov_order):
    '''Create a random sequence of words from probabilities calculated from the training data.
    
    Arguments:
    probabilities --
    markov_order  --
    '''
    selected_key = tuple(['@@pad@@' for _ in range(markov_order)])
    generated_word = to_print = ''

    while generated_word != '@@pad@@':
        to_print += (generated_word + ' ')
        generated_word = Main.choose_next_word(selected_key, probabilities)
        temp = list(selected_key)[1:]
        temp.append(generated_word)
        selected_key = tuple(temp)        
    return to_print[1:len(to_print)-1]


def main(args):
    '''Then entry point to this program.
    
    Arguments:
    args -- a list of specifications to how the program should be run. The format should be:
    - output_file   -- The file to write the result to
    - markov_order  -- The number of words each generated word uses (must be integer greater than 0)
    - training_file -- This is a varargs argument. Each training_file will be used for data to generate words.
    '''
    if len(args) < 2:
        sys.stderr.write("Usage: <markov_order> <training_file> ...")
        return

    try:
        chunk_size = int(args[0])  # the size of each the word chunks that will make up the output
    except ValueError:
        sys.stderr.write('Numerical arguments must be non-negative integers')
        return
    files = args[1:]           # the training files

    # Error Handling
    if chunk_size < 1:
        sys.stderr.write("Markov order must exceed 0")
        return

    '''maps tuples of words maps of the words that are preceded by the tuples in the training docs.
    Each map matches the following-word with the number of times it occurs as a following word'''
    bigram_counts = {}

    try:
        for file_name in files: # for each file passed in, store data from that file in global maps
            process_file(file_name, chunk_size, bigram_counts)
    except IOError:
        print "Invalid file path"
        return
    print "Training data recorded"

    probabilities = {}
    Main.calculate_probabilities(bigram_counts,probabilities) # determine probabilities of generating a word given a previous word
    print "Markov probabilities calculated"

    result = produce_text(probabilities, chunk_size)
    print 'RESULT: ' + result

if __name__ == '__main__': main(sys.argv[1:])