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


def score_similarity(reference, sentence):
    m = MosesTokenizer()
    tr = m.tokenize(reference)
    ts = m.tokenize(sentence)
    # print(tr)
    # print(ts)
    score = 0
    br = list(nltk.bigrams(tr))
    bs = list(nltk.bigrams(ts))
    # print(br)
    # print(bs)
    for x in ts:
        if x in stopwords:
            continue
        if x in tr:
            # print("Matched unigram: " + str(x))
            # tr.remove(x)
            score += len(x)
    for x in bs:
        if x in stopwords:
            continue
        if x in br:
            # print("Matched bigram: " + str(x))
            # br.remove(x)
            score += 3 * (len(x[0]) + len(x[1]))
    return score


def extract() -> None:
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(data_dir):
        if filename.endswith(".story"):
            path = os.path.join(data_dir, filename)
            print("Path: " + path)
            with open(path, "r", encoding="utf-8") as file:
                lines = file.readlines()
                parse(filename, lines)


def parse(file_name: str, lines: List[str]) -> None:
    import re
    hitHighlight: bool = False
    sentences = []
    highlights = []
    for x in lines:
        x = x.strip()
        xs = re.split(r'[.?!"]\s+', x)
        for x in xs:
            if len(x) == 0:
                continue
            if hitHighlight:
                highlights.append(x)
                hitHighlight = False
            elif x == "@highlight":
                hitHighlight = True
            else:
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

    diff = 1
    i = 0
    last_score = scores[sorted[i]]
    counted = 0

    while counted < len(highlights) or diff > 0.8 + 0.03 * counted:
        labels[sorted[i]] = 1
        counted += 1
        i += 1
        next_score = scores[sorted[i]]
        if next_score == 0:
            break
        diff = next_score / last_score
        print("Diff:", diff, next_score, last_score)
        last_score = next_score

    with open(os.path.join(output_dir, file_name), "w+", encoding="utf-8") as f:
        for x in sentences:
            f.write(str(labels[x]) + " " + x + "\n")
        for x in highlights:
            f.write("2 " + x + "\n")


if __name__ == "__main__":
    extract()
