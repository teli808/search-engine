# Zootgle Search Engine

Given a set of web pages, the program tokenizes all visible text from HTML, giving special weight to words in bold, H1, H2, H3, and title tags, then stores in an inverted index.  Every time a certain number of documents have been processed, the indexer offloads to an auxillary file, due to set memory constraints.  Individual index files are merged together later.  The search engine returns based off TF-IDF scoring and cosine similarity.  

# HOW TO RUN
Run the search engine with user_interface.py, but make sure to unzip the precalculated index files first.  If you would like to index the web pages on your own, use indexerfinal.py with the provided web pages.
