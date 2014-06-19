# Language-agnostic extractive summarization using
# graph-based ranking models.

from os import path
from pprint import pprint
import graph
import numpy as np
import re
from MBSP.tokenizer import split as mbsp_split

SRCDIR = path.dirname(path.realpath(__file__))
CORPUSPATH = path.join(SRCDIR,'tests/corpus')
SUMMARIZATIONMETHODS = ['pagerank','hits_auths','hits_hubs']

def build_stop_words_set():
    '''
    Build set of stop words to ignore.
    '''

    # source: http://jmlr.org/papers/volume5/lewis04a/a11-smart-stop-list/english.stop
    return set(open(path.join(SRCDIR,'smartstop.txt'), 'r').read().splitlines())

SMARTSTOPWORDS = build_stop_words_set()

def tokenize_into_sentences(text):
    ''' Tokenizes input text into sentences using the MBSP parser.  '''
    return mbsp_split(text.strip())

def get_bow(sentence):
    ''' Returns a bag of words for the sentence '''
    sentenceWords = re.findall(r"[\w']+", sentence)
    cleanWords = []
    for word in sentenceWords:
        if word not in SMARTSTOPWORDS:
            cleanWords.append(word)
    return set(cleanWords)

def summarize_text(text, n=4, method=SUMMARIZATIONMETHODS[0]):
    ''' Returns a list with n most important strings ranked in decreasing order of page rank. '''

    if method not in SUMMARIZATIONMETHODS:
        raise PageRankNotAvailableException("'method' parameter must be one of the following: %s" % SUMMARIZATIONMETHODS)

    sentenceList = tokenize_into_sentences(text)
    g = graph.Graph()
    for index, sentence in enumerate(sentenceList):
        g.add_sentence(index, get_bow(sentence))

    if method == SUMMARIZATIONMETHODS[0]:
        pageRank = g.get_pagerank()
        ranked_sentences = map(lambda x: sentenceList[x], np.argsort(pageRank)[::-1])
        return ranked_sentences[:n]
    elif method == SUMMARIZATIONMETHODS[1]:
        auth, hubs = g.get_HITS()
        ranked_sentences = map(lambda x: sentenceList[x], np.argsort(auth)[::-1])
        return ranked_sentences[:n]
    else:
        auth, hubs = g.get_HITS()
        ranked_sentences = map(lambda x: sentenceList[x], np.argsort(hubs)[::-1])
        return ranked_sentences[:n]

def summarize_file(file_name, n=4, method=SUMMARIZATIONMETHODS[0]):
    text = open(file_name, 'r').read()
    return summarize_text(text, n, method)

def test_summarization():
    text = open(path.join(CORPUSPATH,'test2.txt'),'r').read()

    print '#### PageRank ###'
    pprint(summarize_text(text))
    print
    print '#### HITS Auths ###'
    pprint(summarize_text(text, method='hits_auths'))
    print
    print '#### HITS Hubs ###'
    pprint(summarize_text(text, method='hits_hubs'))
    print

if __name__ == '__main__':
    test_summarization()

