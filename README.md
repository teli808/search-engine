# Zootgle Search Engine

# Description: 
This search engine is a multi-part program which indexes all web pages from a given directory, scores each document on the basis of TF-IDF and cosine similarity, and ultimately returns the most relevant webpages for a given search query.

Given a set of web pages, the indexer tokenizes all visible text from HTML, giving special weight to words in bold, H1, H2, H3, and title tags, then stores in an inverted index.  After a certain number of documents have been processed, the indexer offloads to an auxillary file, which can be adjusted based on the user's memory constraints.  Individual index files are merged together later.  The search engine component returns top results based off TF-IDF scoring and cosine similarity.  

# Indexing Statistics:
  • I ran this program on the domain (https://www.ics.uci.edu/):
    Number of documents: 55,482
    Size of directory: 2.81 GB 
    Final inverted index size (stored on disk): 322.9 MB
  • Additional information:
    Due to the large amount of pages in this domain, the program offloaded the inverted index to separate files on disk 6
    times during this indexing process and merged them after.

# How to Run
Run indexerfinal 
