import os
from nltk.tokenize.moses import MosesTokenizer, MosesDetokenizer

moses = MosesTokenizer()


def init(ref_dir, score_dir, tokenize=False):
    actual_positives = 0.0
    true_positives = 0.0
    guessed_positives = 0.0
    for filename in os.listdir(score_dir):
        if filename.endswith(".story"):
            path = os.path.join(score_dir, filename)
            ans = os.path.join(ref_dir, filename)
            actuals = []
            preds = []
            length = 0
            with open(ans, "r", encoding="utf-8") as file:
                length, actuals, refs = labels(file)
            with open(path, "r", encoding="utf-8") as file:
                tmp = file.readlines()
                if tokenize:
                    for sentence in tmp:
                        tokens = moses.tokenize(sentence)
                        preds.append(" ".join(tokens))
                else:
                    preds = tmp

            actual_positives += len(actuals)
            guessed_positives += len(preds)

            for x in preds:
                if x in actuals:
                    true_positives += 1.0

            print(filename)
            print(actuals)
            print(preds)
            print(refs)
            print("\n")

    recall = true_positives / actual_positives
    precision = true_positives / guessed_positives

    f1 = 2.0 * precision * recall / (precision + recall)

    print("Total F1 Score: {}".format(f1))
    print("Total Recall: {}".format(recall))
    print("Total Precision: {}".format(precision))
    print("Guessed +: {}".format(guessed_positives))
    print("Actual +: {}".format(actual_positives))
    print("True +: {}".format(true_positives))


def labels(file):
    lines = file.readlines()
    labels = []
    refs = []
    ct = 0
    for line in lines:
        label = line[0: line.index(" ")]
        sentence = line[line.index(" ") + 1:]
        tokens = moses.tokenize(sentence)
        if label == '1':
            labels.append(" ".join(tokens))
            ct += 1
        elif label == '0':
            ct += 1
        elif label == '2':
            refs.append(" ".join(tokens))
    return ct, labels, refs


if __name__ == "__main__":
    # init(ref_dir="../sample_10k", score_dir="./rnn_rnn10")
    # init(ref_dir="../sample_10k", score_dir="./cnn_rnn10")
    # init(ref_dir="../sample_10k", score_dir="./attn_rnn10")
    init(ref_dir="../sample_extracted", score_dir="./mcp", tokenize=True)
