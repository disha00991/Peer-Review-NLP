import collections
import glob
import json
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
pd.set_option('display.max_colwidth', None, 'display.max_rows', None, )

class Dataset:
    def __init__(self):
        dataset_dir = "./datasets/"

        #SUBSETS = "train dev test".split()
        SUBSETS = ["train"]


        self.datasets = collections.defaultdict(list)

        for subset in SUBSETS:
            for filename in glob.glob(dataset_dir + subset + "/*"):
                with open(filename, 'r') as f:
                    self.datasets[subset].append(json.load(f))

        self.all_pairs = sum(self.datasets.values(), [])
        
    def get_data(self):        
        return self.all_pairs
    
    def get_data_info(self):
        def total_and_average_len(list_of_lists):
            big_list = sum(list_of_lists, [])
            return len(big_list), len(big_list)/len(list_of_lists)
        
        def count_dataset(pairs, subset):
            # TODO: Add double-annotated and adjudicated
            review_total, review_average = total_and_average_len([pair["review_sentences"] for pair in pairs])
            rebuttal_total, rebuttal_average = total_and_average_len([pair["rebuttal_sentences"] for pair in pairs])
            return {
                "subset":subset,
                "pairs": len(pairs),
                "forums": len(set(pair["metadata"]["forum_id"] for pair in pairs)),
                "adjudicated": len([pair for pair in pairs if pair["metadata"]["annotator"] == "anno0"]),
                "review_sentences": review_total,
                "rebuttal_sentences": rebuttal_total,
                "review_avg_sentences": review_average,
                "rebuttal_avg_sentences": rebuttal_average,

            }
        # Distribution of examples over sets
        df_dicts = [count_dataset(pairs, subset) for subset, pairs in self.datasets.items()]
        df = pd.DataFrame.from_dict(df_dicts)
        return df
    
    def get_review_df(self):
        df = pd.DataFrame({'review_id':[],'rating':[], 'sentence_index':[], 'text':[], 'coarse':[], 'fine':[], 'asp':[], 'pol':[]},
              columns = ['review_id', 'sentence_index', 'text', 'coarse', 'fine', 'asp', 'pol'])
        for pair in self.all_pairs:
            rs = pd.json_normalize(pair, record_path=['review_sentences'])
            rs['rating'] = pair['metadata']['rating']
            df = df.append(rs)

        return df
    
    def get_rebuttal_df(self):
        df = pd.DataFrame({'review_id':[],'rating':[], 'sentence_index':[], 'text':[], 'coarse':[], 'fine':[]},
              columns = ['review_id', 'sentence_index', 'text', 'coarse', 'fine'])
        for pair in self.all_pairs:
            rs = pd.json_normalize(pair, record_path=['rebuttal_sentences'])
            rs['rating'] = pair['metadata']['rating']
            df = df.append(rs)

        return df

