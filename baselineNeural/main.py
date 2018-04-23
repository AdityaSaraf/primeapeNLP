import torch
from torch import nn, optim
import torch.nn.functional as F
from torch.autograd import Variable

from baselineNeural.data_loader import *


class Net(nn.Module):
    def __init__(self, embedding_dim, input_dim, hidden_size):
        super(Net, self).__init__()
        self.grus = [nn.GRU(input_size=self.embedding_dim,
                            hidden_size=self.hidden_size,
                            batch_first=True)
                     for _ in range(input_dim)]
        for _ in range(input_dim)

        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 16 * 5 * 5)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x


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
        print("lens", len(sentences), len(labels), len(sentences[0]), len(sentences[1]))
        tensor1 = torch.FloatTensor(sentences)
        tensor2 = torch.IntTensor(labels)
        tensor_data.append((tensor1, tensor2))
    print("Finished embeddings.")
    return tensor_data


if __name__ == "__main__":
    print("Loading GLoVe vectors.")
    embedding_dim, glove = load_glove()
    print("Loading training data.")
    train = load_train(debug=True)
    train = embed(glove, train)

    criterion = nn.CrossEntropyLoss()
    net = Net(embedding_dim=embedding_dim, input_dim=len(train), hidden_size=32)
    optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)

    for epoch in range(2):  # loop over the dataset multiple times
        running_loss = 0.0
        for i, data in enumerate(train):
            # get the inputs
            inputs, labels = data
            print(inputs)
            print(labels)

            # wrap them in Variable
            inputs = Variable(inputs)
            labels = Variable(labels)

            print("zero param gradients")
            # zero the parameter gradients
            optimizer.zero_grad()

            print("forward backward opt")
            # forward + backward + optimize
            outputs = net(inputs)

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
