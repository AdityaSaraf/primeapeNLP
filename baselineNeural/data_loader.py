import logging

import numpy as np
from tqdm import tqdm
import mmap

import torch

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
    vocab_size = get_num_lines(url)
    with open(url, encoding="utf-8") as glove_file:
        for line in tqdm(glove_file, total=vocab_size):
            fields = line.strip().split(" ")
            word = fields[0]
            vector = np.asarray(fields[1:], dtype="float32")
            if embedding_dim is None:
                embedding_dim = len(vector)
            else:
                assert embedding_dim == len(vector)
            glove_embeddings[word] = vector

    all_embeddings = np.asarray(list(glove_embeddings.values()))
    embeddings_mean = float(np.mean(all_embeddings))
    embeddings_std = float(np.std(all_embeddings))
    logger.info("Initializing {}-dimensional pretrained embeddings".format(embedding_dim))
    embedding_matrix = torch.FloatTensor(vocab_size, embedding_dim).normal_(embeddings_mean, embeddings_std)
    # Manually zero out the embedding of the padding token (0).
    # embedding_matrix[0].fill_(0)
    # This starts from 1 because 0 is the padding token, which
    # we don't want to modify.
    i = 0
    for word in glove_embeddings:
        # If we don't have a pre-trained vector for this word,
        # we don't change the row and the word has random initialization.
        embedding_matrix[i] = torch.FloatTensor(glove_embeddings[word])
        i += 1
    return embedding_matrix


def load_train(url=TRAIN_URL):
    return _load_inputs(url)


def load_dev(url=DEV_URL):
    return _load_inputs(url)


def load_test(url=TEST_URL):
    return _load_inputs(url)


def _load_inputs(url):
    pass


def get_num_lines(file_path):
    fp = open(file_path, "r+")
    buf = mmap.mmap(fp.fileno(), 0)
    lines = 0
    while buf.readline():
        lines += 1
    return lines
