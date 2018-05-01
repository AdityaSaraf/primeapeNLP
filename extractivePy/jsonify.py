import json

import os

from nltk.tokenize.moses import MosesTokenizer, MosesDetokenizer


def nice_one(dir_name, output_name):
    ls = []
    moses = MosesTokenizer()
    strs = []
    for filename in os.listdir(dir_name):
        if filename.endswith(".story"):
            path = os.path.join(dir_name, filename)
            with open(path, "r", encoding="utf-8") as file:
                lines = file.readlines()
                label_ls = []
                token_ls = []
                summs = []
                for line in lines:
                    label = line[0: line.index(" ")]
                    sentence = line[line.index(" ") + 1:]
                    tokens = moses.tokenize(sentence)
                    if label == '2':
                        summs.append(" ".join(tokens))
                    else:
                        label_ls.append(label)
                        token_ls.append(" ".join(tokens))
                obj = {
                    "name": filename,
                    "doc": "\n".join(token_ls),
                    "labels": "\n".join(label_ls),
                    "summaries": "\n".join(summs)
                }
                json_str = json.dumps(obj)
                print(json_str)
                strs.append(json_str + "\n")
    print("Finished reading .story inputs.")

    with open(output_name, "w", encoding="utf-8") as file:
        file.writelines(strs)


if __name__ == "__main__":
    nice_one("../sample_extracted", output_name="sample_extracted.json")
