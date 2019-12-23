from collections import namedtuple

import os
import json 
import urllib
import math

from parser import *

''' 
Every term in the inverted index is associated with a list of Postings, each of which contains the following info:
DocID: each URL is given a number to be used for easy access in the search component
TFIDF: Short for term frequency-inverse document frequency, this value is an indicator of how important a word is
to a document in a given corpus
'''
Posting = namedtuple("Posting", "docid tfidf")

def run_indexer():
    id_num = initial_index("WEB PAGES", 0, 1)
    doc_id = id_num[0]
    number_of_batches = id_num[1] 
    merger(number_of_batches, "dev_og_index_pos.txt")
    count_to_tfidf("dev_full_index_only_freq.txt", doc_id)
    
def initial_index(file_name: str, doc_id: int, number_of_batches: int) -> (int, int):
    ''' Indexes the given corpus and offloads to a file every 10,000 documents due to set memory constraints. '''

    since_last_batch = 0 #Counter for keeping track of when to offload inverted_index to file
    doc_id_dictionary = {} #Maps every URL with a doc id in key value format doc_id : URL
    seen_url_dict = {} #Used to keep track of duplicate URLs
    positions_dict = {} #Bookkeeping file that stores positions of each term in every offloaded inverted index file
    inverted_index = defaultdict(list) #The inverted index containing term : [list of postings]

    for (root, dirs, files) in os.walk(file_name): #Iterate through all given web pages (stored in .json files)
        for file in files:
            #Offload to a new file every 10,000 documents.  Can be changed based on memory constraints
            if since_last_batch == 10000:
                offload("dev_index" + str(number_of_batches) + ".txt", inverted_index, positions_dict, number_of_batches)
                inverted_index.clear() 
                since_last_batch = 0
                number_of_batches += 1

            #Parse each json file and if it is not a duplicate URL, tokenize and add to inverted_index
            with open(os.path.join(root, file)) as json_file: 
                json_parsed = json.load(json_file)
                if json_parsed["encoding"] == "utf-8" or json_parsed["encoding"] == "ascii":
                    url_tuple = urllib.parse.urldefrag(json_parsed["url"]) #Remove fragment portion of URL
                    if not url_tuple[0] in seen_url_dict: #Only tokenize URLs which have not been seen before
                        doc_id_dictionary[doc_id] = url_tuple[0]
                        tokens_from_html = text_from_html(json_parsed["content"]) #returns a tuple (regular words, imp words) 
                        word_frequencies = computeWordFrequencies(tokenize(tokens_from_html[0]), tokenize(tokens_from_html[1]))
                        for token, frequency in word_frequencies.items():
                            new_posting = Posting(doc_id, frequency)
                            if isAscii(token): #Valid tokens are only made of lowercase & ASCII char
                                inverted_index[token.lower()].append(new_posting)
                                if not token.lower() in positions_dict:
                                    positions_dict[token.lower()] = {}
                        seen_url_dict[url_tuple[0]] = 1 
                        doc_id += 1
                        since_last_batch += 1

    #Offload remaining index to a file and write bookkeeping indexes to separate files as well
    offload("dev_index" + str(number_of_batches) + ".txt", inverted_index, positions_dict, number_of_batches) 
    with open("dev_doc_ids.txt", "w") as doc_id_dict:
        doc_id_dict.write(str(doc_id_dictionary))
    with open("dev_og_index_pos.txt", "w") as index_pos_dict:
        index_pos_dict.write(str(positions_dict))
    #Return a tuple containing number of documents and number of offloaded inverted index files for information purposes
    return (doc_id, number_of_batches)
    
def merger(number_of_batches: int, positions_dict_str: str):
    ''' Merge all inverted index files with their term and Postings lists into one complete inverted index file '''
    read_streams = {}

    #Create a dictionary with a read stream for each inverted index file in format file_number: read_stream
    with open(positions_dict_str, "r") as positions_dict_stream:
        positions_dict = eval(positions_dict_stream.read())
    write_stream = open("dev_full_index_only_freq.txt", "w" #open stream used to write final, merged inverted index
    sorted_terms = sorted(positions_dict.keys())
    for x in range(1, number_of_batches + 1): #
        read_streams[x] = open("dev_index" + str(x) + ".txt", "r")

    '''
    Look at terms beginning from the smallest (alphabetically), merge all files which contain Postings lists for
    that term, then write to the final index.  Repeat the process until there are no more terms.
    '''
    while len(positions_dict) != 0: #once a term is written it is removed from dict 
        smallest_term = sorted_terms.pop(0)
        list_of_postings = []
        for x in range(1, number_of_batches + 1):
            if x in positions_dict[smallest_term]:
                #Use positions dict to seek out the term in each inverted index file
                read_streams[x].seek(positions_dict[smallest_term][x])
                line = eval(read_streams[x].readline())
                list_of_postings.extend(line[1])
        item = (smallest_term, list_of_postings)
        write_stream.write(str(item) + "\n")
        del positions_dict[smallest_term]
    for stream in read_streams.values():
        stream.close()  
    write_stream.close()
 
def offload(file_name: str, data_dict: dict, positions_dict: dict, current_file: int):
    '''
    Function used during the indexing process to write a dictionary (in memory) to disk in tuple format:
    (term, [Postings list])
    with each tuple on one line for easier access later.
    '''
    inverted_index_tuple_list = sorted(data_dict.items(), key = lambda x: x[0]) #sort by term in ascending order
    with open(file_name, "w") as to_offload:
        for item in inverted_index_tuple_list:
            positions_dict[item[0]][current_file] = to_offload.tell()
            to_offload.write(str(item) + "\n") #each item is on its own line
        
def count_to_tfidf(data_dict: str, num_doc: int):
    ''' Convert frequency count to tfidf scoring '''
    read_stream = open(data_dict, "r")
    line = read_stream.readline()
    tfidf_sum = [0] * num_doc #each index for one doc 
    positions_dict = {} #position of each term in the file to be used with search function
    write_stream = open("dev_full_index_with_tfidf.txt", "w")
    while line: 
        term_postings_tuple = eval(line)
        df = len(term_postings_tuple[1]) #number of documents containing the term
        updated_postings_list = []
        for posting in term_postings_tuple[1]:
            tf = posting.tfidf
            tf_idf_calculated = (1 + math.log10(tf)) * math.log10(num_doc/df) #update tfidf, no longer just freq count
            updated_postings_list.append(Posting(posting.docid, tf_idf_calculated))
            tfidf_sum[posting.docid] += tf_idf_calculated
        positions_dict[term_postings_tuple[0]] = write_stream.tell() #position in the updated full index file
        new_tuple = (term_postings_tuple[0], updated_postings_list)
        write_stream.write(str(new_tuple) + "\n") #one term per line
        line = read_stream.readline()
    read_stream.close()
    write_stream.close() 
    for x in range(len(tfidf_sum)):
        tfidf_sum[x] = math.sqrt(tfidf_sum[x])
    with open("dev_doc_len_list.txt", "w") as doc_len_list:
        doc_len_list.write(str(tfidf_sum))
    with open("dev_final_pos_dict.txt", "w") as pos_dict:
        pos_dict.write(str(positions_dict))

run_indexer()