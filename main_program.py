'''
Created on Dec 2, 2019

@author: tylerli
'''
import search_component_final

def main():
    print("Please wait, loading...")
    with open("dev_doc_len_list.txt", "r") as doc_len_list:
        doc_len_loaded = eval(doc_len_list.read())
    with open("dev_final_pos_dict.txt", "r") as pos_dict:
        pos_dict_loaded = eval(pos_dict.read())
    with open("dev_doc_ids.txt", "r") as doc_id_name:
        doc_ids = eval(doc_id_name.read())
    while True: 
        print()
        user_query = input("Please input a search query or !quit to exit: ")
        if user_query == "!quit":
            return
        search_component_final.search_results(str(user_query), doc_len_loaded, "dev_full_index_with_tfidf.txt", pos_dict_loaded, doc_ids, len(doc_ids))
    
main()