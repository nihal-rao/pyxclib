"""
    Generate vectorized text and tf-idf for given text
"""
import os
import sys
import numpy as np
from xclib.text import text_utils
from xclib.data import data_utils
from sklearn.feature_extraction.text import TfidfVectorizer as tfidf
import scipy.sparse as sp
import pickle


def read_split_file(split_fname):
    '''
        Return array of train/ test split
        Args:
            split_fname: str: split file with 0/1 in each line
        Returns:
            np.array: split
    '''
    return np.genfromtxt(split_fname, dtype=np.int)


def _split_data(data, indices):
    """
        Handles list and sparse/dense matrices
        Args:
            data: list of matrix
            indices: indices to choose
        Returns:
            chosen data in the same format
    """
    return list(map(lambda x: data[x], indices))


def split_train_test(features, split):
    '''
        Split a list of text in train and text set
        0: train, 1: test
        Args:
            features: list or dense or sparse matrix
            labels: list or dense or sparse matrix
            split: numpy array with 0/1 split
        Returns:
            train_feat, train_labels: train features and labels
            test_feat, test_labels: test features and labels
    '''
    train_idx = np.where(split == 0)[0].tolist()
    test_idx = np.where(split == 1)[0].tolist()
    return features[train_idx], features[test_idx]


def main():
    data_dir = sys.argv[1]
    data = sys.argv[2]
    # text feature object
    t_obj = tfidf(min_df=3, max_df=0.9, stop_words=[], norm=None)
    text = t_obj.fit_transform(open(data, 'r', encoding='latin1'))
    num_instances = text.shape[0]
    data_not_present = np.where(np.ravel(text.sum(axis=1)) == 0)[0]

    print("DATA is not present in %d documents" % len(data_not_present))

    text = sp.hstack([text, np.zeros((num_instances, 1), np.float32)]).tocsr()
    vocab = t_obj.get_feature_names()+['unk']
    np.savetxt(data_dir+'/Xf-Text.txt', vocab, fmt="%s")

    text[data_not_present, -1] = 0
    flags = np.ones((num_instances, 1), np.int32)
    flags[data_not_present, 0] = 0

    train_txt, test_txt = split_train_test(text, read_split_file(sys.argv[3]))
    train_lbl, test_lbl = split_train_test(
    data_utils.read_sparse_file(sys.argv[4]), read_split_file(sys.argv[3]))
    train_dp, test_dp = split_train_test(flags, read_split_file(sys.argv[3]))

    tr_lb = train_lbl[train_dp[:, 0] != 0]
    ts_lb = test_lbl[test_dp[:, 0] != 0]
    print(tr_lb.shape, train_txt.shape)
    print(ts_lb.shape, test_txt.shape)
    data_utils.write_data(sys.argv[5], (train_txt.tocsr()[train_dp[:, 0] != 0]).astype(
        np.float32), tr_lb.astype(np.float32))
    data_utils.write_data(sys.argv[6], (test_txt.tocsr()[test_dp[:, 0] != 0]).astype(
        np.float32), ts_lb.astype(np.float32))


if __name__ == '__main__':
    main()
