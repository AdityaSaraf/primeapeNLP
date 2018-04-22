#!/usr/bin/env python

""" Split data in extracted/ to extracted/train, extracted/dev, and extracted/test """

import os
import random

from math import ceil
from typing import List, Tuple

extract_dir = "../extracted/"
train_dir = "../extracted/train"
dev_dir = "../extracted/dev"
test_dir = "../extracted/test"


def read_names(dir=extract_dir):
    set = []
    for filename in os.listdir(dir):
        set.append((dir, filename))
    return set


def separate(names: List[str],
             train_ratio=0.75,
             dev_ratio=0.10,
             test_ratio=0.15) -> Tuple[List[str], List[str], List[str]]:
    """
    Split given list of strings into three sets.
    """
    train = []
    dev = []
    test = []
    random.shuffle(names)
    length = len(names)
    n1 = ceil(length * train_ratio)
    n2 = ceil(length * dev_ratio)
    n3 = ceil(length * test_ratio)
    assert train_ratio + dev_ratio + test_ratio - 1 < 1e-5
    while n1 > 0 and names:
        train.append(names.pop())
        n1 -= 1
    while n2 > 0 and names:
        dev.append(names.pop())
        n2 -= 1
    while n3 > 0 and names:
        test.append(names.pop())
        n3 -= 1
    return train, dev, test


def move(files, dest):
    count = 0
    total = len(files)
    if not os.path.exists(dest):
        os.makedirs(dest)
    for pair in files:
        count += 1
        if count % 2500 == 0:
            print("Moved {}/{}".format(count, total))
        dir = pair[0]
        filename = pair[1]
        full_path = os.path.join(dir, filename)
        dest_path = os.path.join(dest, filename)
        os.rename(full_path, dest_path)


if __name__ == "__main__":
    print("Reading file names...")
    names = read_names()
    print("Finished reading files.")
    train, dev, test = separate(names)
    print("Created train, dev, and test sets of sizes:", len(train), len(dev), len(test))
    print("Moving train...")
    move(train, train_dir)
    print("Moving dev...")
    move(dev_dir, dev_dir)
    print("Moving test...")
    move(test, test_dir)
