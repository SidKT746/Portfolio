# -*- coding: utf-8 -*-
"""SRI_KAN.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1m9kuwgJpyhyk4qLcvySto3j_8LZQnzJZ
"""

!pip install gdown
!gdown https://drive.google.com/uc?id=1za7rq7UKET6NWxBxyduXDAnZ5RAHGqtA

#https://drive.google.com/file/d/1za7rq7UKET6NWxBxyduXDAnZ5RAHGqtA/view?usp=sharing

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('2018-06-06-ss.cleaned.csv')

df = df[['seq','len','sst3']][(df['len']<40)&(df['has_nonstd_aa']==False)]
df.drop_duplicates(subset='seq',inplace=True)

def clear_asterisks(df, seqs_column_name, pct=30):
    indices = []
    for i, seq in enumerate(df[seqs_column_name]):
        if (seq.count('*')*100/len(seq)) <= pct: indices.append(i)
    return df.iloc[indices]

df = clear_asterisks(df,'seq')
df[0:50]

import pandas as pd
import random

# Function to contaminate sequences
def contaminate_sequences(df, contamination_factor):
    # List of possible amino acids
    amino_acids = 'ACDEFGHIKLMNPQRSTVWY'

    def contaminate_seq(seq, factor):
        seq_list = list(seq)
        for i in range(len(seq_list)):
            if random.random() < factor:
                seq_list[i] = random.choice(amino_acids)
        return ''.join(seq_list)

    # Apply contamination
    df['seq'] = df['seq'].apply(lambda x: contaminate_seq(x, contamination_factor))

    return df

# Example usage
contamination_factor = 0.4
#contaminate_df = contaminate_sequences(df, contamination_factor)
df[0:50]

def ngrams(seq,n=3):
    return ([seq[i:i+n] for i in range(len(seq)-n+1)])

df['seqss']=df['seq'].apply(ngrams)
df.head()

# function to calculate maximum length
# we could simply use df['len'].max(), but let's compute it just in case
def max_length(series):
    l = []
    [l.append(len(s)) for s in series]
    return max(l)

maxlen = max_length(df['seq'])
maxlen

# tokenize, then pad sequences into uniform length
from tensorflow.keras.preprocessing import text, sequence
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.utils import to_categorical

tok_x = Tokenizer(lower=False)
tok_x.fit_on_texts(df['seqss'].values)
xAll = tok_x.texts_to_sequences(df['seqss'].values)
xAll = sequence.pad_sequences(xAll, maxlen=maxlen, padding='post')
#print(xAll)

tok_y = Tokenizer(char_level=True)
tok_y.fit_on_texts(df['sst3'].values)
yAll = tok_y.texts_to_sequences(df['sst3'].values)
yAll = sequence.pad_sequences(yAll, maxlen=maxlen, padding='post')
#print(xAll)
yAll = to_categorical(yAll)


randomNums = []
numItems = 100

for i in range(numItems):
    num = np.random.randint(0,5425)
    while num in randomNums:
        num = np.random.randint(0,5425)
    randomNums.append(num)


x = xAll[randomNums] #x = x[randomNums]
y = yAll[randomNums]

xTest = []
yTest = []

for i in range(50):
    num = np.random.randint(0,5425)
    while num in randomNums:
        num = np.random.randint(0,5425)
    randomNums.append(num)
    xTest.append(df.iloc[num]['seq'])
    yTest.append(df.iloc[num]['sst3'])

#x.shape, y.shape

print(tok_y.word_index)

print(xTest)
print(yTest)

# split data into train and test sets
from sklearn.model_selection import train_test_split

x_tr, x_ts, y_tr, y_ts = train_test_split(x,y,test_size=0.25, random_state=33)
x_tr.shape, y_tr.shape, x_ts.shape, y_ts.shape

a = 0
b = 0
c = 0
d = 0

for i in y_ts:
  for j in i:
    if j[0] == 1:
      a += 1
    elif j[1] == 1:
      b += 1
    elif j[2] == 1:
      c += 1
    elif j[3] == 1:
      d += 1
print(a,b,c,d)

#import libraries and calculate hyperparameters about train-data dimensions
from keras.models import Sequential
from keras.layers import Embedding, Dense, TimeDistributed, Bidirectional, GRU, LSTM
n_ngrams = len(tok_x.word_index) + 1
n_tags = len(tok_y.word_index) + 1

print(n_ngrams, n_tags)

#!pip install Deep-KAN

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from math import ceil
from deepkan import SplineLinearLayer, ChebyshevKANLayer, RBFKANLayer
import tensorflow as tf
import keras.backend as K

# Assuming x_tr, y_tr, x_ts, y_ts are already processed and available as numpy arrays

# Convert data to tensors
x_tr = torch.tensor(x_tr, dtype=torch.long)  # Input should be long for Embedding
y_tr = torch.tensor(y_tr, dtype=torch.float32)  # Output should be float for BCEWithLogitsLoss

x_ts = torch.tensor(x_ts, dtype=torch.long)
y_ts = torch.tensor(y_ts, dtype=torch.float32)

embedding_dim = n_ngrams//12  # Output dimension from Embedding layer
maxlen = 39  # Input length
n_tags = 4  # Number of classes for each position
learning_rate = 0.01
weight_decay = 0.001

SplineKAN = nn.Sequential(
    nn.Embedding(num_embeddings=n_ngrams, embedding_dim=embedding_dim, padding_idx=0),  # Padding index is 0
    nn.Flatten(),  # Flatten the output of the Embedding layer
    SplineLinearLayer(maxlen * embedding_dim, 25),
    SplineLinearLayer(25, maxlen * n_tags)
)

ChebyshevKAN = nn.Sequential(
    nn.Embedding(num_embeddings=n_ngrams, embedding_dim=embedding_dim, padding_idx=0),  # Padding index is 0
    nn.Flatten(),  # Flatten the output of the Embedding layer
    ChebyshevKANLayer(maxlen * embedding_dim, 25, 4),
    ChebyshevKANLayer(25, maxlen * n_tags, 4)
)

RBFKAN = nn.Sequential(
    nn.Embedding(num_embeddings=n_ngrams, embedding_dim=embedding_dim, padding_idx=0),  # Padding index is 0
    nn.Flatten(),  # Flatten the output of the Embedding layer
    RBFKANLayer(maxlen * embedding_dim, 25),
    RBFKANLayer(25, maxlen * n_tags)
)

MLP = nn.Sequential(
    nn.Embedding(num_embeddings=n_ngrams, embedding_dim=embedding_dim, padding_idx=0),  # Padding index is 0
    nn.Flatten(),  # Flatten the output of the Embedding layer
    nn.Linear(maxlen * embedding_dim, 25),
    nn.ReLU(),
    nn.Linear(25, maxlen * n_tags),  # Output shape is (batch_size, maxlen * n_tags)
)

loss_fn = nn.BCEWithLogitsLoss()  # For multi-label classification


def calculate_accuracy(y_pred, y_true):
    with torch.no_grad():
        y_pred = (y_pred > 0.5).float()  # Threshold predictions to 0 or 1
        correct = (y_pred == y_true).float().sum()  # Count correct predictions
        total = y_true.numel()  # Total number of elements in target tensor
        accuracy = correct / total
    return accuracy.item()

def q3_acc(y_true, y_pred):
    y_true = y_true.detach().numpy()
    y_pred = y_pred.detach().numpy()
    y = tf.argmax(y_true, axis=-1)
    y_ = tf.argmax(y_pred, axis=-1)
    accuracy = 0
    for i in range(39):
      if y[0][i] == y_[0][i]:
        accuracy += 1
    return accuracy/39

def train(model, x_tr, y_tr, optimizer, loss_fn, batch_size):
    model.train()
    total_loss = 0
    total_accuracy = 0
    reps = ceil(len(x_tr) / batch_size)
    for i in range(0, len(x_tr), batch_size):
        Xbatch = x_tr[i:i+batch_size]
        ybatch = y_tr[i:i+batch_size]

        # Forward pass
        y_pred = model(Xbatch)  # Shape: (batch_size, maxlen * n_tags)
        y_pred = y_pred.view(-1, maxlen, n_tags)  # Reshape to (batch_size, maxlen, n_tags)

        # Loss calculation
        loss = loss_fn(y_pred, ybatch)  # Compute loss
        total_loss += loss.item()

        # Accuracy calculation
        accuracy = q3_acc(y_pred, ybatch)
        total_accuracy += accuracy

        # Backpropagation
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    avg_loss = total_loss / reps
    avg_accuracy = total_accuracy / reps
    return avg_loss, avg_accuracy

def validate(model, x_ts, y_ts, loss_fn, batch_size):
    model.eval()
    reps = ceil(len(x_ts) / batch_size)
    with torch.no_grad():
        total_loss = 0
        total_accuracy = 0
        for i in range(0, len(x_ts), batch_size):
            Xbatch = x_ts[i:i+batch_size]
            ybatch = y_ts[i:i+batch_size]

            # Forward pass
            y_pred = model(Xbatch)  # Shape: (batch_size, maxlen * n_tags)
            y_pred = y_pred.view(-1, maxlen, n_tags)  # Reshape to (batch_size, maxlen, n_tags)

            # Loss calculation
            loss = loss_fn(y_pred, ybatch)  # Compute loss
            total_loss += loss.item()

            # Accuracy calculation
            accuracy = q3_acc(y_pred, ybatch)
            total_accuracy += accuracy

        avg_loss = total_loss / reps
        avg_accuracy = total_accuracy / reps
        return avg_loss, avg_accuracy

# Function to get predictions
def get_predictions(model, x_ts, batch_size):
    model.eval()
    all_preds = []
    with torch.no_grad():
        for i in range(0, len(x_ts), batch_size):
            Xbatch = x_ts[i:i+batch_size]
            y_pred = model(Xbatch)  # Shape: (batch_size, maxlen * n_tags)
            y_pred = y_pred.view(-1, maxlen, n_tags)  # Reshape to (batch_size, maxlen, n_tags)
            y_pred = torch.sigmoid(y_pred)  # Apply sigmoid to get probabilities
            all_preds.append(y_pred.cpu().numpy())
    return np.vstack(all_preds)  # Combine all batches into a single array

# Function to calculate TP, TN, FP, FN, precision, and recall
def calculate_metrics(preds, y_true, threshold=0.5):
    preds = (preds > threshold).astype(int)  # Binarize predictions at the threshold
    y_true = y_true.cpu().numpy()  # Convert true labels to numpy array if they are torch tensors

    # Reshape predictions and true labels to (num_samples * maxlen, n_tags)
    preds = preds.reshape(-1, n_tags)
    y_true = y_true.reshape(-1, n_tags)

    TP = (preds * y_true).sum(axis=0)
    TN = ((1 - preds) * (1 - y_true)).sum(axis=0)
    FP = (preds * (1 - y_true)).sum(axis=0)
    FN = ((1 - preds) * y_true).sum(axis=0)

    precision = TP / (TP + FP + 1e-8)
    recall = TP / (TP + FN + 1e-8)

    return TP, TN, FP, FN, precision, recall

print(MLP)

optimizer = optim.RMSprop(MLP.parameters(), lr=learning_rate, weight_decay=weight_decay)

MLPACCURACY = []

for epoch in range(10):  # Number of epochs
    train_loss, train_acc = train(MLP, x_tr, y_tr, optimizer, loss_fn, 1)  # Batch size of 1
    val_loss, val_acc = validate(MLP, x_ts, y_ts, loss_fn, 1)  # Batch size of 1
    MLPACCURACY.append(val_acc)

    print(f'Epoch {epoch+1}, Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}, Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}')

# Get predictions
preds = get_predictions(MLP, x_ts, 1)  # Use batch size of 1

# Calculate metrics
TP, TN, FP, FN, precision, recall = calculate_metrics(preds, y_ts)

# Print the results
for i in range(n_tags):
    print(f'Class {i}:')
    print(f'  TP: {TP[i]}, TN: {TN[i]}, FP: {FP[i]}, FN: {FN[i]}')
    print(f'  Precision: {precision[i]:.4f}, Recall: {recall[i]:.4f}')

print(SplineKAN)

optimizer = optim.RMSprop(SplineKAN.parameters(), lr=learning_rate, weight_decay=weight_decay)

SPLINEACCURACY = []

for epoch in range(10):  # Number of epochs
    train_loss, train_acc = train(SplineKAN, x_tr, y_tr, optimizer, loss_fn, 1)  # Batch size of 1
    val_loss, val_acc = validate(SplineKAN, x_ts, y_ts, loss_fn, 1)  # Batch size of 1
    SPLINEACCURACY.append(val_acc)

    print(f'Epoch {epoch+1}, Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}, Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}')

# Get predictions
preds = get_predictions(SplineKAN, x_ts, 1)  # Use batch size of 1

# Calculate metrics
TP, TN, FP, FN, precision, recall = calculate_metrics(preds, y_ts)

# Print the results
for i in range(n_tags):
    print(f'Class {i}:')
    print(f'  TP: {TP[i]}, TN: {TN[i]}, FP: {FP[i]}, FN: {FN[i]}')
    print(f'  Precision: {precision[i]:.4f}, Recall: {recall[i]:.4f}')

print(ChebyshevKAN)

optimizer = optim.RMSprop(ChebyshevKAN.parameters(), lr=learning_rate, weight_decay=weight_decay)

CHEBYSHEVACCURACY = []

for epoch in range(100):  # Number of epochs
    train_loss, train_acc = train(ChebyshevKAN, x_tr, y_tr, optimizer, loss_fn, 1)  # Batch size of 1
    val_loss, val_acc = validate(ChebyshevKAN, x_ts, y_ts, loss_fn, 1)  # Batch size of 1
    CHEBYSHEVACCURACY.append(val_acc)

    print(f'Epoch {epoch+1}, Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}, Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}')

# Get predictions
preds = get_predictions(ChebyshevKAN, x_ts, 1)  # Use batch size of 1

# Calculate metrics
TP, TN, FP, FN, precision, recall = calculate_metrics(preds, y_ts)

# Print the results
for i in range(n_tags):
    print(f'Class {i}:')
    print(f'  TP: {TP[i]}, TN: {TN[i]}, FP: {FP[i]}, FN: {FN[i]}')
    print(f'  Precision: {precision[i]:.4f}, Recall: {recall[i]:.4f}')

print(RBFKAN)

optimizer = optim.RMSprop(RBFKAN.parameters(), lr=learning_rate, weight_decay=weight_decay)

RBFACCURACY = []

for epoch in range(10):  # Number of epochs
    train_loss, train_acc = train(RBFKAN, x_tr, y_tr, optimizer, loss_fn, 1)  # Batch size of 1
    val_loss, val_acc = validate(RBFKAN, x_ts, y_ts, loss_fn, 1)  # Batch size of 1
    RBFACCURACY.append(val_acc)

    print(f'Epoch {epoch+1}, Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}, Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}')

# Get predictions
preds = get_predictions(RBFKAN, x_ts, 1)  # Use batch size of 1

# Calculate metrics
TP, TN, FP, FN, precision, recall = calculate_metrics(preds, y_ts)

# Print the results
for i in range(n_tags):
    print(f'Class {i}:')
    print(f'  TP: {TP[i]}, TN: {TN[i]}, FP: {FP[i]}, FN: {FN[i]}')
    print(f'  Precision: {precision[i]:.4f}, Recall: {recall[i]:.4f}')

import matplotlib.pyplot as plt

plt.plot(SPLINEACCURACY, label='KAN')
plt.plot(CHEBYSHEVACCURACY, label='CHEBYSHEV')
plt.plot(RBFACCURACY, label='RBF')

plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()
plt.show()