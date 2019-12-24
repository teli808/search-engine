# Zootgle Search Engine

This search engine is a multi-part program which indexes all web pages from a given directory, scores each document on the basis of TF-IDF and cosine similarity, and ultimately returns the most relevant webpages for a given search query. 

# Indexing Statistics:
  • Program was run on the domain (https://www.ics.uci.edu/):

    Number of documents: 55,482
    Size of directory: 2.81 GB 
    Final inverted index size (stored on disk): 322.9 MB
		
  • Due to the large amount of pages in this domain and memory constraints, the program offloaded the inverted index to separate files on disk 6 times and merged them at the end.  

# How to Run:  
Indexer component: Run **indexer_final.py** with the directory **WEB PAGES**.  For faster indexing, I included a smaller set of subdomains compared to what I ran on.

Search engine component: Run **user_interface.py** after unzipping **precalculated_files.zip**.

