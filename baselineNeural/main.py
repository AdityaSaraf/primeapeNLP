import mmap

import numpy as np
import torch
from nltk.tokenize.moses import MosesTokenizer
from torch import nn, optim
import torch.nn.functional as F
from torch.autograd import Variable
from tqdm import tqdm
import logging


# from baselineNeural.data_loader import load_train, load_glove


class Baseline(nn.Module):
    def __init__(self, embedding_dim, input_dim, hidden_size):
        super(Baseline, self).__init__()
        self.embedding_dim = embedding_dim
        self.input_dim = input_dim
        self.hidden_size = hidden_size

        self.gru = nn.GRU(input_size=self.input_dim,
                          hidden_size=self.hidden_size,
                          batch_first=True)
        # self.grus = [nn.GRU(input_size=self.embedding_dim,
        #                     hidden_size=self.hidden_size,
        #                     batch_first=True)
        #              for _ in range(input_dim)]
        self.lineboi = nn.Linear(self.hidden_size, self.input_dim)

    def forward(self, sentences):
        print("HERE")
        sentences = sentences.unsqueeze(1)
        sentences = torch.transpose(sentences, 0, 2)
        print(sentences)
        print(len(sentences))
        print("HERE2")
        print(self.input_dim, self.hidden_size, self.embedding_dim)
        # 50x1x32 and 1x50x32
        encoded_sentences, _ = self.gru(sentences)
        print("encoded:")
        print(encoded_sentences)
        seq = self.lineboi(encoded_sentences)

        return seq


class Net(nn.Module):
    def __init__(self, embedding_dim, input_dim, hidden_size):
        super(Net, self).__init__()
        self.gru = nn.GRU(input_size=self.input_dim,
                          hidden_size=self.hidden_size,
                          batch_first=True)
        # self.grus = [nn.GRU(input_size=self.embedding_dim,
        #                     hidden_size=self.hidden_size,
        #                     batch_first=True)
        #              for _ in range(input_dim)]
        self.compress = nn.Linear(16 * 5 * 5, 120)

    def forward(self, sentences):
        return


def embed(glove, train):
    embed_dimensions = len(next(iter(glove.values())))
    # unk = np.zeros(embed_dimensions, dtype="float32")
    new_data = []
    longest_sentence_count = 0
    longest_word_count = 0
    for data in train:
        # one document
        sentences, labels = data
        # track highest num of sentences in a doc
        if len(sentences) > longest_sentence_count:
            longest_sentence_count = len(sentences)
        embedded_sentences = []
        for sentence in sentences:
            # convert sentences to list of word embeddings
            embedded_sentence = []
            # track longest sentence length
            if len(sentence) > longest_word_count:
                longest_word_count = len(sentence)
            # embed word
            for word in sentence:
                if word in glove:
                    embedded_sentence.append(glove[word])
                else:
                    embedded_sentence.append([0 for _ in range(embed_dimensions)])
            # save embedded sentence
            embedded_sentences.append(embedded_sentence)
        # store tuple of embedded sentences and labels
        new_data.append((embedded_sentences, labels))
    # tensor_data converts everything to tensors
    tensor_data = []
    for sentences, labels in tqdm(new_data):
        # print(sentences)
        # print(sentences is None)
        # print(len(sentences))
        # length = len(sentences)
        # print("length", length)
        # pad number of sentences in doc
        while len(sentences) < longest_sentence_count:
            # default sentence = list of a single unk word
            sentences.append([[0 for _ in range(embed_dimensions)]])
        # pad labels to match above
        while len(labels) < longest_sentence_count:
            labels.append(0)
        # pad sentences to match longest sentence
        for sentence in sentences:
            while len(sentence) < longest_word_count:
                sentence.append([0 for _ in range(embed_dimensions)])
        # print("lens", len(sentences), len(labels), len(sentences[0]), len(sentences[1]))

        # this seems wrong but for a baseline I guess it'll do
        compressed_ss = []
        for sentence in sentences:
            compressed_s = [0 for _ in range(embedding_dim)]
            for word in sentence:
                for i, val in enumerate(word):
                    # print("sentences: ", sentences)
                    # print("sentence: ", sentence)
                    # print("val: ", val)
                    compressed_s[i] += val
            compressed_ss.append(compressed_s)

        # tensor1 = torch.FloatTensor(sentences)
        tensor1 = torch.FloatTensor(compressed_ss)
        tensor2 = torch.IntTensor(labels)
        tensor_data.append((tensor1, tensor2))
    print("Finished embeddings.")
    return longest_sentence_count, tensor_data


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
            vals = []
            for x in fields[1:]:
                vals.append(float(x))
            # vector = np.asarray(fields[1:], dtype="float32")
            vector = vals
            if embedding_dim is None:
                embedding_dim = len(vector)
            else:
                assert embedding_dim == len(vector)
            glove_embeddings[word] = vector
    return embedding_dim, glove_embeddings


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
        if debug and i > 100:
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


if __name__ == "__main__":
    print("Loading GLoVe vectors.")
    embedding_dim, glove = load_glove()
    print("Loading training data.")
    # TODO: make this a DataLoader
    train = load_train(debug=True)
    input_dim, train = embed(glove, train)

    # net = Net(embedding_dim=embedding_dim, input_dim=len(train), hidden_size=32)
    net = Baseline(embedding_dim=embedding_dim, input_dim=input_dim, hidden_size=32)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)

    for epoch in range(2):  # loop over the dataset multiple times
        running_loss = 0.0
        for i, document in enumerate(train):
            # get the inputs
            sentences, labels = document
            print(sentences)
            print(labels)

            # wrap them in Variable
            sentences = Variable(sentences)
            labels = Variable(labels)

            print("zero param gradients")
            # zero the parameter gradients
            optimizer.zero_grad()

            print("forward backward opt")
            # forward + backward + optimize
            outputs = net(sentences)
            print("OUTPUTS: ", outputs)

            print("loss back")
            loss = criterion(outputs, labels)
            loss.backward()

            print("step")
            optimizer.step()

            # print statistics
            running_loss += loss.data[0]
            # if i % 2000 == 1999:  # print every 2000 mini-batches
            if i % 2 == 0:  # print every 2000 mini-batches
                print('[%d, %5d] loss: %.3f' %
                      (epoch + 1, i + 1, running_loss / 2000))
                running_loss = 0.0

        print('Finished Training')
