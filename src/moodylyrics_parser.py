from utils.dataset_parsing import *

if __name__ == '__main__':
  import pandas as pd
  import numpy as np
  import os
  import io
  import threading
  from utils.progress import progress

  moodyl = pd.read_csv('datasets/moodylyrics_cleaned.csv')
  
  # Split the dataset in 4 parts and run 4 parallel threads for doing this
  rows = list() # Rows of our dataset
  total = len(moodyl)
  count = 0
  for idx, row in moodyl.iterrows():
    fname = '_'.join([row['Emotion'], row['Artist'], row['Song']])
    fname = os.path.join('ml_lyrics', fname)
    if os.path.lexists(fname):
      with io.open(fname, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
        lyric_doc = nlp(content)
        title_doc = nlp(row['Song'])
        
        lyric = preprocess(content)#lyric_doc.text)
        features = feature_extraction(lyric, row['Song'])

        freq = features['frequencies'] 
        elem = (
          row['Artist'], row['Song'],
          lyric_doc.vector, title_doc.vector,
          features['line_count'], features['word_count'],#get_line_count(lyric), get_word_count(lyric),
          #get_slang_counts(lyric),
          features['echoisms'], features['selfish'],#get_echoisms(lyric), get_selfish_degree(lyric),
          count_duplicate_lines(lyric), features['is_title_in_lyrics'],# (row['Song'], lyric),
          features['rhymes'],#get_rhymes(lyric),
          features['verb_tenses']['present'], features['verb_tenses']['past'], features['verb_tenses']['future'], #verb_freq['present'], verb_freq['past'], verb_freq['future'],
          freq['ADJ'], freq['ADP'], freq['ADV'], freq['AUX'], freq['CONJ'], 
          freq['CCONJ'], freq['DET'], freq['INTJ'], freq['NOUN'], freq['NUM'],
          freq['PART'], freq['PRON'], freq['PROPN'], freq['PUNCT'], freq['SCONJ'],
          freq['SYM'], freq['VERB'], freq['X'], freq['SPACE'],
          row['Emotion']
        )
        
        rows.append(elem)
        count += 1
        progress(count, total, '{}/{}'.format(count, total))
  df = pd.DataFrame(rows)

  output_path = 'datasets/moodylyrics_featurized.csv'
  df.to_csv(output_path)
  print()
  print('Done! Dataset written:', output_path)