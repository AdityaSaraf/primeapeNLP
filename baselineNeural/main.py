import torch
from torch import nn, optim
import torch.nn.functional as F
from torch.autograd import Variable

from baselineNeural.data_loader import *


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
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


net = Net()


def embed(glove, train):
    embed_dimensions = len(next(iter(glove.values())))
    unk = np.zeros(embed_dimensions, dtype="float32")
    new_data = []
    longest = 0
    longest_sentence = 0
    for data in train:
        inputs, labels = data
        if len(inputs) > longest:
            longest = len(inputs)
        embed_inputs = []
        for input in inputs:
            embed_input = []
            if len(input) > longest_sentence:
                longest_sentence = len(input)
            for word in input:
                if word in glove:
                    embed_input.append(np.array(glove[word], dtype="float32"))
                else:
                    embed_input.append(unk)
            embed_inputs.append(embed_input)
        new_data.append((np.array(embed_inputs), labels))
    tensor_data = []
    print("LONGEST", longest)
    for inputs, labels in tqdm(new_data):
        while len(inputs) < longest:
            inputs = np.append(inputs, [unk])
            # inputs.append([unk])
        for input in inputs:
            while len(input) < longest_sentence:
                input.append(unk)
        while len(labels) < longest:
            labels.append(0)
        print(inputs[0])
        print(inputs[1])
        print("lens", len(inputs), len(labels), len(inputs[0]), len(inputs[1]))
        tensor1 = torch.FloatTensor(inputs)
        tensor2 = torch.IntTensor(labels)
        tensor_data.append((tensor1, tensor2))
    print("Finished embeddings.")
    return new_data


if __name__ == "__main__":
    print("Loading GLoVe vectors.")
    glove = load_glove()
    print("Loading training data.")
    train = load_train(debug=True)
    train = embed(glove, train)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)

    for epoch in range(2):  # loop over the dataset multiple times
        running_loss = 0.0
        for i, data in enumerate(train):
            # get the inputs
            inputs, labels = data

            # wrap them in Variable
            inputs, labels = Variable(inputs), Variable(labels)

            # zero the parameter gradients
            optimizer.zero_grad()

            # forward + backward + optimize
            outputs = net(inputs)

            loss = criterion(outputs, labels)
            loss.backward()

            optimizer.step()

            # print statistics
            running_loss += loss.data[0]
            # if i % 2000 == 1999:  # print every 2000 mini-batches
            if i % 2 == 0:  # print every 2000 mini-batches
                print('[%d, %5d] loss: %.3f' %
                      (epoch + 1, i + 1, running_loss / 2000))
                running_loss = 0.0

        print('Finished Training')
