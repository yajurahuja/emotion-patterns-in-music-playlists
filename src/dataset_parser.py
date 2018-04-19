import regex as re

import spacy
import pronouncing
from wiktionaryparser import WiktionaryParser

import time

nlp = spacy.load('en_core_web_lg')
nlp.vocab.add_flag(lambda s: s.lower() in spacy.lang.en.stop_words.STOP_WORDS, spacy.attrs.IS_STOP)

parser = WiktionaryParser()

def preprocess(doc):
  # Delete text between parentheses
  prep = doc
  re.sub("([\(\[])(.*?)([\)\]])", "", prep)
  # Split by line
  prep = prep.split('\n')
  # Delete empty lines
  prep = [ln for ln in prep if ln != '']
  return prep

def feature_extraction(lines, title):
  wc = get_word_count(lines)
  lc = get_line_count(lines)

  verbfreq = dict()
  verbfreq['present'] = 0
  verbfreq['future'] = 0
  verbfreq['past'] = 0

  freq = dict()

  d = {
    'word_count': wc, 'line_count': lc,
    'echoisms': 0, 'slangs': 0, 'rhymes': 0,
    'verb_tenses': verbfreq, 'frequencies': freq,
    'selfish': 0, 'is_title_in_lyrics': False
  }
 
  tags = ['ADJ', 'ADP', 'ADV', 'AUX', 'CONJ', 'CCONJ', 'DET', 'INTJ', 'NOUN', 
    'NUM', 'PART', 'PRON', 'PROPN', 'PUNCT', 'SCONJ', 'SYM', 'VERB', 'X', 'SPACE']
  for tag in tags:
    freq[tag] = 0

  vowels = ['a', 'e', 'i', 'o', 'u']
   
  verbs_no = 0
  
  pronouns_count, i_count = 0, 0

  for line in lines:
    # Echoisms
    # Do echoism count on a word level
    doc = nlp(line)
    
    for i in range(len(doc)):
      # Echoisms
      if i < len(doc) - 1:
        d['echoisms'] += doc[i].text.lower() == doc[i+1].text.lower()
      tk = doc[i]     
      # Count echoisms inside words e.g. yeeeeeeah
      for j in range(len(tk.text) - 1):
        if tk.text[j] == tk.text[j+1] and tk.text in vowels:
          d['echoisms'] += 1
          break
      # Selfish degree
      if tk.pos_ == 'PRON':
        pronouns_count += 1
        if tk.text == 'I':
          i_count += 1
      # Verb frequencies
      token = doc[i]
      if token.pos_ == 'VERB' and token.tag_ != 'MD': 
        verbs_no += 1
        if 'present' in spacy.explain(token.tag_):
          verbfreq['present'] += 1
        elif 'past' in spacy.explain(token.tag_):
          verbfreq['past'] += 1 
      elif token.pos_ == 'VERB' and token.tag_ == 'MD' and token.text.lower() == 'will':
        if i < len(doc) - 1:
          i += 1
          next_token = doc[i]
          if next_token is not None and next_token.text == 'VB':
            verbs_no += 1
            verbfreq['future'] += 1
      # Tag frequency
      if doc[i].pos_ in tags:
        freq[doc[i].pos_] += 1
      # Title in lyrics
      if doc[i].text == title:
        d['is_title_in_lyrics'] = True
  
  
 
  for key in freq:
    freq[key] /= wc
  
  d['selfish'] = i_count / pronouns_count if pronouns_count > 0 else 0
  if verbs_no > 0:
    for key, value in freq.items():
      freq[key] = value/verbs_no
  d['echoisms'] /= wc
  return d

def get_line_count(tokens):
  return len(tokens) + 1

def get_word_count(tokens):
  count = 0
  for line in tokens:
    count += len(line.split(' '))
  return count

def get_rhymes(lines):
  # returns the number of rhymes in a lyric
  count = 0
  for i in range(len(lines)-1):
    words = lines[i].split()
    if len(words) < 1:
      continue
    rhymes = pronouncing.rhymes(words[-1])
    next_line_words = lines[i+1].split()
    if next_line_words is not None and len(next_line_words) > 0 and  next_line_words[-1] in rhymes:
      count += 1 
  return count / get_line_count(lines) 

def get_slang_counts(tokens):
  slang_counter = 0
  for tk in tokens:
    for word in tk:
      wiki_word = parser.fetch(word)
      if len(wiki_word) > 0:
        definitions = wiki_word[0]['definitions']
        if len(definitions) > 0:
          slang_counter += 'slang' in parser.fetch(word)[0]['definitions'][0]['text'].lower()
  return slang_counter / get_word_count(tokens)

def get_echoisms(tokens):
  vowels = ['a', 'e', 'i', 'o', 'u']
  # Do echoism count on a word level
  echoism_count = 0
  for line in tokens:
    doc = nlp(line)
    for i in range(len(doc) - 1):
      echoism_count += doc[i].text.lower() == doc[i+1].text.lower()
    # Count echoisms inside words e.g. yeeeeeeah
    for tk in doc:     
      for i in range(len(tk.text) - 1):
        if tk.text[i] == tk.text[i+1] and tk.text in vowels:
          echoism_count += 1
          break
  return echoism_count / get_word_count(tokens)

def get_verb_tense_frequencies(lines):
  freq = dict()
  freq['present'] = 0
  freq['future'] = 0
  freq['past'] = 0
  verbs_no = 0

  for line in lines:
    doc = nlp(line)
    for i in range(len(doc)):
      token = doc[i]
      if token.pos_ == 'VERB' and token.tag_ != 'MD': 
        verbs_no += 1
        if 'present' in spacy.explain(token.tag_):
          freq['present'] += 1
        elif 'past' in spacy.explain(token.tag_):
          freq['past'] += 1 
      elif token.pos_ == 'VERB' and token.tag_ == 'MD' and token.text.lower() == 'will':
        if i < len(doc) - 1:
          i += 1
          next_token = doc[i]
          if next_token is not None and next_token.text == 'VB':
            verbs_no += 1
            freq['future'] += 1
        
  if verbs_no > 0:
    for key, value in freq.items():
      freq[key] = value/verbs_no

  return freq 

def get_frequencies(tokens):
  tags = ['ADJ', 'ADP', 'ADV', 'AUX', 'CONJ', 'CCONJ', 'DET', 'INTJ', 'NOUN', 
    'NUM', 'PART', 'PRON', 'PROPN', 'PUNCT', 'SCONJ', 'SYM', 'VERB', 'X', 'SPACE']
  freq = dict()
  for tag in tags:
    freq[tag] = 0
  for line in tokens:
    doc = nlp(line)
    for word in doc:
      if word.pos_ in tags:
        freq[word.pos_] += 1
  wc = get_word_count(tokens)
  for key in freq:
    freq[key] /= wc
  return freq

def get_selfish_degree(tokens):
  pronouns_count, i_count = 0, 0
  for line in tokens:
    doc = nlp(line)
    for tk in doc:
      if tk.pos_ == 'PRON':
        pronouns_count += 1
        if tk.text == 'I':
          i_count += 1
  return i_count / pronouns_count if pronouns_count > 0 else 0

def count_duplicate_lines(tokens):
  return sum([tokens.count(x) for x in list(set(tokens)) if tokens.count(x) > 1]) / get_word_count(tokens)

def is_title_in_lyrics(title, tokens):
  for tk in tokens:
    if title in tk:
      return True
  return False

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
        lyric_doc = nlp(f.read())
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
          freq['SYM'], freq['VERB'], freq['X'], freq['SPACE']
        )
        
        rows.append(elem)
        count += 1
        progress(count, total, '{}/{}'.format(count, total))
  df = pd.DataFrame(rows)

  df.to_csv('test.csv')
