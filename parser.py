from collections import defaultdict

from nltk.stem import PorterStemmer
from bs4 import BeautifulSoup
from bs4.element import Comment

def tokenize(text: str) -> list:
    ''' Tokenizes all sequences of 2 or more lowercase alphanumeric and/or ASCII characters '''
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
    ps = PorterStemmer() #words are stemmed to increase accuracy of search algorithm
    token_dict = defaultdict(int)
    for word in ListNormal:
        word = ps.stem(word).lower()
        token_dict[word] = token_dict[word] + 1 #every word is originally given a weight of 1
    for word in ListImportant:
        word = ps.stem(word).lower()
        token_dict[word] = token_dict[word] + 0.2  #add extra 0.2 weight for words tagged in bold, h1, h2, h3, or title
    return token_dict

def isAscii(word: str) -> bool:
    ''' Checks if given word is made of all ASCII characters '''
    return len(word) == len(word.encode())

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def text_from_html(content) -> (str, str):
    ''' Returns visible text from an html file and important words '''
    soup = BeautifulSoup(content, 'html.parser')
    important_words = ""

    ''' Important words are classified with the tags below, and are weighted accordingly in computeWordFrequencies '''
    for x in soup.find_all(['b', 'h1', 'h2', 'h3', 'title']):
        important_words += str(x.text) + " "

    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return (u" ".join(t.strip() for t in visible_texts), important_words)