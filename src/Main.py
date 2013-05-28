''' Markov Random Text Generator

Created on May 24, 2013
@author: Bryce Aebi

Provided 1 or more training documents, this program will create 'random' yet intelligible text. Training 
documents are used to record word data. That is, for each unique word in the training documents, the variety
of words that followed that word in the training documents will be recorded along with the probability of their 
occurrence with respect to all of the other possible following words.

Given a target number of words to generate. This program will probabilistically choose each subsequent word to generate
based on previously generated words. The number of previous words each generated word is based on is determined
by the user defined markov-order argument. (Ex: if this equaled 2, then each word would be generated based
on the two preceding words in the already-generated text)
'''

import sys
import random

def process_file(file_name, markov_order, bigram_counts):
    '''Stores the word occurrence data from a file in the global dictionary bigram_counts.
    
    Arguments:
    file_name         -- the path to the file to read
    markov_order      -- the markov order (ex: if markov_order = 2, each generated word is based on the two previous words)
    bigram_counts     -- maps tuples of words maps of the words that are preceded by the tuples in the training docs.
                         Each map matches the following-word with the number of times it occurs as a following word
    '''
    with open(file_name,'r') as text:
        line = text.readline()
        line_chunks = line.split()

        while (True):
            while len(line_chunks) < markov_order+1:
                line = text.readline()
                if not line:
                    return
                line_chunks.extend(line.split())
            prev_words = line_chunks[0:markov_order]
            generated_word = line_chunks[markov_order]
            update_bigram_counts(tuple(prev_words), generated_word,bigram_counts)
            line_chunks = line_chunks[1:]


def update_bigram_counts(prev_words, word, bigram_counts):
    '''Record the occurrence of following_word after word in a global dictionary bigram_counts.
    
    Arguments:
    prev_words    -- the Markov-order length sequence of words preceding a word
    word          -- the word preceded by prev_words
    bigram_counts -- maps tuples of words maps of the words that are preceded by the tuples in the training docs.
                     Each map matches the following-word with the number of times it occurs as a following word
    '''
    if bigram_counts.has_key(prev_words):
        word_count_map = bigram_counts[prev_words]
        count = word_count_map.get(word,0)
        word_count_map[word] = count+1
    else:
        bigram_counts[prev_words] = {word: 1}


def calculate_probabilities(bigram_counts, probabilities):
    '''For each word in the corpus, determines the probabilities of the next possible words. Stores results in probabilities.
    
    Arguments:
    bigram_counts -- maps tuples of words maps of the words that are preceded by the tuples in the training docs.
                     Each map matches the following-word with the number of times it occurs as a following word
    probabilities -- a map of word tuples to maps of words (generated by that tuple) to their probabilities
    '''
    for (prev_words, following_word_map) in bigram_counts.items():
        total_words = sum(following_word_map.values())
        probabilities[prev_words] = {}
        for (w,count) in following_word_map.items():
            probabilities[prev_words][w] = float(count)/total_words


def produce_text(output_file, output_size, probabilities):
    '''Using the calculated word sequence probabilities, generates random text with output_size words and writes it to output_file.
    
    Arguments:
    output_file       -- the path to the file to write the output to
    output_size       -- the number of words to write to the output
    probabilities     -- a map of word tuples to maps of words (generated by that tuple) to their probabilities
    '''
    with open (output_file,'w') as output:
        rand_index = random.randint(0, len(probabilities.keys())-1)
        last_words = probabilities.keys()[rand_index]
        to_print = ''

        for i in range(output_size):
            next_word = choose_next_word(last_words, probabilities)
            temp = list(last_words)[1:]
            temp.append(next_word)
            last_words = tuple(temp)
            to_print += (' '+ next_word)
            if i%100 == 0:
                output.write(to_print)
                to_print = ''

        output.write(to_print)


def choose_next_word(last_words, probabilities):
    '''Given a tuple of words, randomly generate the next word.
    
    Arguments:
    last_words    -- a tuple of words that precede the to-be-generated word
    probabilities -- a map of word tuples to maps of words (generated by that tuple) to their probabilities
    '''
    next_word_map = probabilities[last_words]
    rand = random.random()
    prob_sum = 0.0
    final_word = ''
    for (next_word, prob) in next_word_map.items():
        final_word = next_word
        prob_sum += prob
        if rand <= prob_sum:
            return next_word

    assert prob_sum <= 1
    return final_word


def main(args):
    '''Then entry point to this program.
    
    Arguments:
    args -- a list of specifications to how the program should be run. The format should be:
    - output_file   -- The file to write the result to
    - num_words     -- The number of words to generate in the output (must be non-negative integer)
    - markov_order  -- The number of words each generated word uses (must be integer greater than 0)
    - training_file -- This is a varargs argument. Each training_file will be used for data to generate words.
    '''
    if len(args) < 4:
        sys.stderr.write("Usage: <outputfile> <num_words> <num_words_per_chunk> <training_file> ...")
        return

    output_file = args[0]      # the file to print the results to
    try:
        output_size = int(args[1]) # the number of words to print to the output file
        chunk_size = int(args[2])  # the size of each the word chunks that will make up the output
    except ValueError:
        sys.stderr.write('Numerical arguments must be non-negative integers')
        return
    files = args[3:]           # the training files

    # Error Handling
    if chunk_size < 1:
        sys.stderr.write("Number of words per generated chunk must exceed 0")
        return
    if output_size < 0:
        sys.stderr.write("The number of words to be generated must be a positive integer")
        return
    
    '''maps tuples of words maps of the words that are preceded by the tuples in the training docs.
    Each map matches the following-word with the number of times it occurs as a following word
    '''
    bigram_counts = {}
        
    try:
        for file_name in files: # for each file passed in, store data from that file in global maps
            process_file(file_name, chunk_size, bigram_counts)
    except IOError:
        print "Invalid file path"
        return
    print "Training data recorded"

    probabilities = {}
    calculate_probabilities(bigram_counts,probabilities) # determine probabilities of generating a word given a previous word
    print "Markov probabilities calculated"

    produce_text(output_file, output_size, probabilities)
    print "Output printed to", output_file


if __name__ == '__main__': main(sys.argv[1:])


