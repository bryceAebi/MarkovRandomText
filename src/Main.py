'''
Created on May 24, 2013

@author: bryce
'''

import sys
import random

'''bigram_counts maps a word to a map of the words that follow it in the 
corpus. Each map matching the following-word with the number of 
times it occurs as a following word
'''
bigram_counts = {}

def process_file(file_name, chunk_size):
    '''Stores the word occurrence data from a file in the global dictionary bigram_counts.
    
    @param: file_name the path to the file to read
    '''
    with open(file_name,'r') as text:
        line = text.readline()
        line_chunks = line.split()

        while (True):
            while len(line_chunks) < chunk_size+1:
                line = text.readline()
                if not line:
                    return
                line_chunks.extend(line.split())
            following_words = line_chunks[1:chunk_size+1]
            assert len(following_words) == chunk_size
            update_bigram_counts(line_chunks[0], tuple(following_words))
            line_chunks = line_chunks[1:]


def update_bigram_counts(word, following_words):
    '''Record the occurrence of following_word after word in a global dictionary bigram_counts.'''
    if bigram_counts.has_key(word):
        word_count_map = bigram_counts[word]
        count = word_count_map.get(following_words,0)
        word_count_map[following_words] = count+1
    else:
        bigram_counts[word] = {following_words: 1}


def calculate_probabilities(bigrams,probabilities):
    '''For each word in the corpus, determines the probabilities of the next possible words. Stores results in probabilities.'''
    for (word, following_words_map) in bigrams.items():
        total_words = sum(following_words_map.values())
        probabilities[word] = {}
        for (w,count) in following_words_map.items():
            probabilities[word][w] = float(count)/total_words


def produce_text(output_file, output_size, probabilities):
    '''Using the calculated word sequence probabilities, generates random text with output_size words and writes it to output_file.'''
    with open (output_file,'w') as output:
        rand_index = random.randint(0, len(probabilities.keys())-1)
        first_word = probabilities.keys()[rand_index]
        counter = 0
        to_print = first_word
        last_word = first_word
        print output_size
        for _ in range(output_size):
            next_words = choose_next_words(last_word, probabilities)
            last_word = next_words[len(next_words)-1]
            counter += 1
            for word in next_words:
                to_print += (' '+ word)
            if counter > 100:
                output.write(to_print)
                to_print = ''
                counter = 0
        output.write(to_print)


def choose_next_words(last_word, probabilities):
    next_words_map = probabilities[last_word]
    rand = random.random()
    prob_sum = 0.0
    final_words = []
    for (next_words, prob) in next_words_map.items():
        final_words = list(next_words)
        prob_sum += prob
        if rand <= prob_sum:
            return list(next_words)

    assert prob_sum <= 1
    return final_words


def main():
    if len(sys.argv) < 5:
        print "Usage: <outputfile> <num_words> <num_words_per_chunk> <training_file> ..."
        return

    output_file = sys.argv[1]      # the file to print the results to
    output_size = int(sys.argv[2]) # the number of words to print to the output file
    chunk_size = int(sys.argv[3])  # the size of each the word chunks that will make up the output
    files = sys.argv[4:]           # the training files

    if chunk_size < 1:
        print "Number of words per generated chunk must exceed 0"
        return
    if output_size < 0:
        print "The number of words to be generated must be a positive integer"
        return
    if chunk_size > output_size:
        print "The number of words to be generated cannot be less than the number of words per generated chunk"
        return
    
    for file_name in files: # for each file passed in, store data from that file in global maps
        process_file(file_name, chunk_size)
    print "Training data recorded"

    probabilities = {}
    calculate_probabilities(bigram_counts,probabilities) # determine probabilities of generating a word given a previous word
    print "Markov probabilities calculated"

    produce_text(output_file, output_size, probabilities)
    print "Output printed to", output_file


if __name__ == '__main__': main()


