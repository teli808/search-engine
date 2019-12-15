'''
Created on Dec 2, 2019

@author: tylerli
'''

from collections import defaultdict
from collections import namedtuple

import os
import json 
import urllib
import math

from nltk.stem import PorterStemmer 
from bs4 import BeautifulSoup
from bs4.element import Comment

#ANALYST: number of documents is 1130
#DEV: number of documents is 50553 
Posting = namedtuple("Posting", "docid tfidf")

def main():
    id_num = initial_index("DEV", 0, 1)
    doc_id = id_num[0]
    number_of_batches = id_num[1] 
    merger(number_of_batches, "dev_og_index_pos.txt")
    count_to_tfidf("dev_full_index_only_freq.txt", doc_id)
    

def initial_index(file_name: str, doc_id: int, number_of_batches: int) -> (int, int): #doc_id, number_of_batches
    since_last_batch = 0
    doc_id_dictionary = {} #need to keep mapping of ids to urls
    seen_url_dict = {} 
    positions_dict = {}
    inverted_index = defaultdict(list) #str, posting
    for (root, dirs, files) in os.walk(file_name):
        for file in files:
            if since_last_batch == 10000: #can be changed 
                offload("dev_index" + str(number_of_batches) + ".txt", inverted_index, positions_dict, number_of_batches)
                inverted_index.clear() 
                since_last_batch = 0
                number_of_batches += 1
            with open(os.path.join(root, file)) as json_file: 
                json_parsed = json.load(json_file)
                if json_parsed["encoding"] == "utf-8" or json_parsed["encoding"] == "ascii":
                    url_tuple = urllib.parse.urldefrag(json_parsed["url"])
                    if not url_tuple[0] in seen_url_dict: #checks if url has been added yet 
                        doc_id_dictionary[doc_id] = url_tuple[0] #doc_id: url
                        tokens_from_html = text_from_html(json_parsed["content"]) #returns a tuple (regular words, imp words) 
                        word_frequencies = computeWordFrequencies(tokenize(tokens_from_html[0]), tokenize(tokens_from_html[1]))
                        for token, frequency in word_frequencies.items():
                            new_posting = Posting(doc_id, frequency)
                            if isAscii(token):
                                inverted_index[token.lower()].append(new_posting) #lowercase and ascii only
                                if not token.lower() in positions_dict:
                                    positions_dict[token.lower()] = {}
                        seen_url_dict[url_tuple[0]] = 1 
                        doc_id += 1  #only add to doc_id if not a duplicate
                        since_last_batch += 1
    offload("dev_index" + str(number_of_batches) + ".txt", inverted_index, positions_dict, number_of_batches) 
    with open("dev_doc_ids.txt", "w") as doc_id_dict:
        doc_id_dict.write(str(doc_id_dictionary))
    with open("dev_og_index_pos.txt", "w") as index_pos_dict:
        index_pos_dict.write(str(positions_dict))
    return (doc_id, number_of_batches)
        
    
def merger(number_of_batches: int, positions_dict_str: str):
    read_streams = {} #file number: read stream 
    with open(positions_dict_str, "r") as positions_dict_stream:
        positions_dict = eval(positions_dict_stream.read())
    write_stream = open("dev_full_index_only_freq.txt", "w")
    sorted_terms = sorted(positions_dict.keys())
    for x in range(1, number_of_batches + 1): 
        read_streams[x] = open("dev_index" + str(x) + ".txt", "r")
    while len(positions_dict) != 0: #once a term is written it is removed from dict 
        smallest_term = sorted_terms.pop(0)
        list_of_postings = []
        for x in range(1, number_of_batches + 1):
            if x in positions_dict[smallest_term]:
                read_streams[x].seek(positions_dict[smallest_term][x]) #go to where this term is in the file
                line = eval(read_streams[x].readline()) #read the line with the term
                list_of_postings.extend(line[1])
        item = (smallest_term, list_of_postings)
        write_stream.write(str(item) + "\n")
        del positions_dict[smallest_term]
    for stream in read_streams.values():
        stream.close()  
    write_stream.close()
 
def offload(file_name: str, data_dict: dict, positions_dict: dict, current_file: int):
    inverted_index_tuple_list = sorted(data_dict.items(), key = lambda x: x[0]) #sort by term in ascending order
    with open(file_name, "w") as to_offload:
        for item in inverted_index_tuple_list:
            positions_dict[item[0]][current_file] = to_offload.tell()
            to_offload.write(str(item) + "\n") #each item is on its own line
        
def count_to_tfidf(data_dict: str, num_doc: int):
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
            tf_idf_calculated = (1 + math.log10(tf)) * math.log10(num_doc/df)#update tfidf, no longer just freq count
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
    

def tokenize(text: str) -> list:
    token_list = []
    temp = ""
    if text == "":
        return token_list
    for character in text:
        character = character.lower()
        if (character.isalpha() or character.isdigit()) and character.isascii():
            temp = temp + character
        else:
            if (temp != "") and (len(temp) > 2):
                token_list.append(temp)
            temp = ""
    if temp != "":
        token_list.append(temp)
    return token_list


def computeWordFrequencies(ListNormal: list, ListImportant: list) -> defaultdict:
    ps = PorterStemmer()
    token_dict = defaultdict(int)
    for word in ListNormal:
        word = ps.stem(word).lower()
        token_dict[word] = token_dict[word] + 1
    for word in ListImportant:
        word = ps.stem(word).lower()
        token_dict[word] = token_dict[word] + 0.2
    return token_dict

def wordCount(dictionary: defaultdict) -> int:
    counter = 0
    for key in dictionary.keys():
        counter += 1
    return counter

def isAscii(word: str) -> bool:
    return len(word) == len(word.encode())

def tag_visible(element):   #Function from StackOverflow
    if element.parent.name in ['style', 'script', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def text_from_html(content) -> (str, str):    #Function from StackOverflow    
    soup = BeautifulSoup(content, 'html.parser')
    important_words = ""
    for x in soup.find_all(['b', 'h1', 'h2', 'h3', 'title']):
        important_words += str(x.text) + " "
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return (u" ".join(t.strip() for t in visible_texts), important_words)
    

main()