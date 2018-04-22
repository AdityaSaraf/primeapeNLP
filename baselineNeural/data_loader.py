import logging
import mmap

import numpy as np
from nltk.tokenize.moses import MosesTokenizer
from tqdm import tqdm

GLOVE_URL = "../glove/glove.6B.50d.txt"

TRAIN_URL = "../extracted/train"
DEV_URL = "../extracted/dev"
TEST_URL = "../extracted/test"

logger = logging.getLogger(__name__)


def load_glove(url=GLOVE_URL):
    """
    Create an embedding matrix for a Vocabulary.
    """
    glove_embeddings = {}
    embedding_dim = None
    logger.info("Reading GloVe embeddings from {}".format(url))

    with open(url, encoding="utf-8") as glove_file:
        for line in tqdm(glove_file, total=get_num_lines(url)):
            fields = line.strip().split(" ")
            word = fields[0]
            vector = np.asarray(fields[1:], dtype="float32")
            if embedding_dim is None:
                embedding_dim = len(vector)
            else:
                assert embedding_dim == len(vector)
            glove_embeddings[word] = vector
    return glove_embeddings


def load_train(url=TRAIN_URL, debug=False):
    return _load_inputs(url, debug)


def load_dev(url=DEV_URL, debug=False):
    return _load_inputs(url, debug)


def load_test(url=TEST_URL, debug=False):
    return _load_inputs(url, debug)


def _load_inputs(url, debug=False):
    m = MosesTokenizer()
    import os
    result = []
    i = 0
    for filename in tqdm(os.listdir(url)):
        i += 1
        if debug and i > 1000:
            break
        if filename.endswith(".story"):
            curr_l = []
            curr_t = []
            path = os.path.join(url, filename)
            with open(path, "r", encoding="utf-8") as file:
                for line in file:
                    label = int(line[:2].strip())
                    if label == 2:
                        continue
                    text = line[2:].strip()
                    tokens = m.tokenize(text)
                    curr_l.append(label)
                    curr_t.append(tokens)
            result.append((curr_t, curr_l))
    return result


def get_num_lines(file_path):
    fp = open(file_path, "r+")
    buf = mmap.mmap(fp.fileno(), 0)
    lines = 0
    while buf.readline():
        lines += 1
    return lines
