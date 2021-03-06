import torch
from torch import nn, optim
from torch.autograd import Variable
from tqdm import tqdm

# from baselineNeural.data_loader import load_train, load_glove
from baselineNeural.data_loader import load_glove, load_train


class Baseline(nn.Module):
    def __init__(self, embedding_dim, input_dim, hidden_size):
        super(Baseline, self).__init__()
        self.embedding_dim = embedding_dim
        self.input_dim = input_dim
        self.hidden_size = hidden_size

        # seq_len = number of inputs in input var
        # input_size = number of FEATURES per input
        self.gru = nn.GRU(input_size=self.embedding_dim,
                          hidden_size=self.hidden_size,
                          batch_first=True)
        # self.grus = [nn.GRU(input_size=self.embedding_dim,
        #                     hidden_size=self.hidden_size,
        #                     batch_first=True)
        #              for _ in range(input_dim)]
        # self.lineboi = nn.Linear(self.hidden_size, self.input_dim)
        self.lineboi = nn.Linear(self.hidden_size, 1)
        self.softmax = nn.Softmax()

    def forward(self, sentences):
        # print("HERE")
        sentences = sentences.unsqueeze(1)
        # sentences = torch.transpose(sentences, 0, 2)
        # print(sentences)
        # print(len(sentences))
        # print("HERE2")
        # print(self.input_dim, self.hidden_size, self.embedding_dim)
        # 50x1x32 and 1x50x32
        encoded_sentences, _ = self.gru(sentences)
        # print("encoded:")
        # print(encoded_sentences)
        seq = self.lineboi(encoded_sentences)
        softmaxed = self.softmax(seq)

        return softmaxed


def embed(glove, train):
    embed_dimensions = len(next(iter(glove.values())))
    # unk = np.zeros(embed_dimensions, dtype="float32")
    new_data = []
    longest_sentence_count = 0
    longest_word_count = 0
    for data in tqdm(train, desc="Embedding sentences"):
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
    for sentences, labels in tqdm(new_data, desc="Converting to Tensors"):
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
        # tensor2 = torch.IntTensor(labels)
        tensor2 = torch.FloatTensor(labels)
        tensor_data.append((tensor1, tensor2))
    return longest_sentence_count, tensor_data


if __name__ == "__main__":
    # print("Loading GLoVe vectors.")
    embedding_dim, glove = load_glove()
    # print("Loading training data.")
    # TODO: make this a DataLoader
    train = load_train(debug=True, dlimit=10000)
    input_dim, train = embed(glove, train)

    # net = Net(embedding_dim=embedding_dim, input_dim=len(train), hidden_size=32)
    net = Baseline(embedding_dim=embedding_dim, input_dim=input_dim, hidden_size=32)
    # criterion = nn.CrossEntropyLoss()
    criterion = nn.BCELoss()
    optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)

    for epoch in range(2):  # loop over the dataset multiple times
        print("epoch")
        running_loss = 0.0
        # TODO: this treats each document as a batch and probably isn't the best way to do it
        # TODO: use DataLoader!!
        for i, document in enumerate(train):
            # get the inputs
            sentences, labels = document

            # wrap them in Variable
            sentences = Variable(sentences)
            labels = Variable(labels)

            # print("zero param gradients")
            # zero the parameter gradients
            optimizer.zero_grad()

            # print("forward backward opt")
            # forward + backward + optimize
            outputs = net(sentences)
            # print("OUTPUTS: ", outputs)
            # print("labels", labels.shape)
            outputs = outputs.squeeze()
            # print("outputs", outputs.shape)

            # print("loss back")
            # loss = criterion(outputs, labels)
            loss = criterion(outputs, labels)
            loss.backward()
            # print("LOSS:", loss)

            # print("step")
            optimizer.step()

            # print statistics
            running_loss += loss.data[0]
            # print("loss data[0] = ", loss.data, loss.data[0])
            # print("running loss", running_loss)
            # if i % 2000 == 1999:  # print every 2000 mini-batches
            print_ct = 5
            if i % print_ct == 0:  # print every 5 mini-batches
                print('[%d, %5d] loss: %.3f' %
                      (epoch + 1, i + 1, running_loss / print_ct))
                running_loss = 0.0

        print('Finished Training')
