import os

import nltk

nltk.download('perluniprops')
nltk.download('nonbreaking_prefixes')
nltk.download('stopwords')

from nltk.tokenize.moses import MosesTokenizer
from typing import List

output_dir = "../extracted/"
data_dir = "../data/"

from nltk.corpus import stopwords

stopwords = set(stopwords.words('english'))

print("Using stopwords: ", stopwords)

m = MosesTokenizer()


def score_similarity(reference, sentence):
    score = 0
    ur = m.tokenize(reference)
    us = m.tokenize(sentence)
    br = list(nltk.bigrams(ur))
    bs = list(nltk.bigrams(us))
    tr = list(nltk.trigrams(ur))
    ts = list(nltk.trigrams(us))
    for x in us:
        if x in stopwords:
            continue
        if x in ur:
            score += len(x)
            # print("Matched unigram: " + str(x))
    for x in bs:
        if x in br:
            score += 3 * (len(x[0]) + len(x[1]))
            # print("Matched bigram: " + str(x))
    for x in ts:
        if x in tr:
            score += 5 * (len(x[0]) + len(x[1]) + len(x[2]))
            # print("Matched trigram: " + str(x))
    return score


def extract(file_list=None) -> None:
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if file_list is None:
        for filename in os.listdir(data_dir):
            if filename.endswith(".story"):
                path = os.path.join(data_dir, filename)
                print("Path: " + path)
                with open(path, "r", encoding="utf-8") as file:
                    lines = file.readlines()
                    parse(filename, lines)
    else:
        for filename in file_list:
            path = os.path.join(data_dir, filename)
            print("Path: " + path)
            with open(path, "r", encoding="utf-8") as file:
                lines = file.readlines()
                parse(filename, lines)


def parse(file_name: str, lines: List[str]) -> None:
    import re
    hit_highlight: bool = False
    sentences = []
    highlights = []
    for x in lines:
        x = x.strip()
        if len(x) == 0:
            continue
        if hit_highlight:
            highlights.append(x)
            hit_highlight = False
            continue

        # print(x, x == "@highlight")
        if x == "@highlight":
            hit_highlight = True
            continue
        # xs = re.split(r'[.?!]\s+', x)
        xs = re.split(r'(?<=[.?!])\s+', x)
        for x in xs:
            if len(x) > 0:
                sentences.append(x)
    if len(highlights) == 0 or len(sentences) == 0:
        print("Skipping empty input.")
        return
    scores = {}
    for x in sentences:
        score = 0
        for h in highlights:
            score += score_similarity(h, x)
        scores[x] = score

    labels = {x: 0 for x in sentences}

    sorted = sentences[:]
    sorted.sort(key=lambda x: scores[x], reverse=True)

    # for x in scores:
    #     print(str(scores[x]), x)
    # print(sorted)

    i = 0
    last_score = scores[sorted[i]]

    len_sorted = len(sorted) / 2
    if len_sorted == 0:
        len_sorted = len(sorted)
    len_highlights = len(highlights)

    while i < len_sorted:
        labels[sorted[i]] = 1
        i += 1

        if i >= len_sorted:
            break

        next_score = scores[sorted[i]]
        if next_score == 0:
            break

        diff = next_score / last_score
        print(" Diff:", diff, next_score, last_score)
        last_score = next_score

        if i > len_highlights and diff < 0.8 + 0.03 * i:
            break

    with open(os.path.join(output_dir, file_name), "w+", encoding="utf-8") as f:
        for x in sentences:
            f.write(str(labels[x]) + " " + x + "\n")
        for x in highlights:
            f.write("2 " + x + "\n")


if __name__ == "__main__":
    extract()
    # extract([
    #     "00a5c6a8b1b3bd07c52e0c64f09350e1190474a7.story",
    #     "008fc24ca9f4c48a54623bef423a3f2f8db8451a.story",
    #     "000064fee589e5607c1534a69f852d37b4936cca.story"
    # ])
