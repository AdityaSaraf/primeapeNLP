import os
from nltk.tokenize.moses import MosesTokenizer, MosesDetokenizer
from tqdm import tqdm

moses = MosesTokenizer()


def init(dir, target):
    if not os.path.exists(target):
        os.makedirs(target)

    for filename in tqdm(os.listdir(dir)):
        if filename.endswith(".story"):
            path = os.path.join(dir, filename)
            with open(path, "r", encoding="utf-8") as file:
                out_path = os.path.join(target, filename)
                with open(out_path, "w", encoding="utf-8") as out:
                    lines = file.readlines()
                    for line in lines:
                        label = line[0: line.index(" ")]
                        sentence = line[line.index(" ") + 1:]
                        tokens = moses.tokenize(sentence)
                        out_line = label + " " + " ".join(tokens) + "\n"
                        out.write(out_line)


if __name__ == "__main__":
    init(dir="../sample_10k", target="../sample_10k_tok")
