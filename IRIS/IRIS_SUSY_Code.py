# -*- coding: utf-8 -*-
"""IRIS_SUSY.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1y-eKSjRm-StkSUdr4BNz5JHoJVry7PcL
"""

# Commented out IPython magic to ensure Python compatibility.
# %pip install pykan
# %pip install matplotlib
# %pip install torch
# %pip install numpy
# %pip install pandas
# %pip install scikit-learn
# %pip intstall tqdm

from kan import KAN
import matplotlib.pyplot
import torch
import numpy
import pandas
from sklearn.preprocessing import MinMaxScaler

# Get program to use GPU
device = "cuda:0" if torch.cuda.is_available() else "cpu"

print(device)

processes = ['SUSY', 'SM']

data_NN = {} # define empty dictionary to hold dataframes that will be used to train the NN

data_NN = {"SUSY": {},
           "SM": {}}


NN_inputs = [
             'lead_lep_pt',
             'sublead_lep_pt',
             'lead_lep_eta',
             'sublead_lep_eta',
             'lead_lep_phi',
             'sublead_lep_phi',
             'missing_energy_magnitude',
             'missing_energy_phi',
             'MET_rel',
             'axial_MET',
             'M_R',
             'M_TR_2',
             'R',
             'MT2',
             'S_R',
             'M_Delta_R',
             'dPhi_r_b',
             'cos(theta_r1)',
             'NN_output'
            ] # list of variables for Neural Network

eventsList = pandas.read_csv("IRISData/SUSY.csv").values.tolist()

for process in processes:
    for input in NN_inputs:
        data_NN[process][input] = []

for process in processes:
    for i in range(len(eventsList)):
        for j in range(0, len(NN_inputs) - 1):
            if process == "SUSY" and eventsList[i][0] == 1:
                data_NN[process][NN_inputs[j]].append(eventsList[i][j+1])
            else:
                data_NN[process][NN_inputs[j]].append(eventsList[i][j+1])

# Convert data into single list
sample_events = []
test_events = []
discovery_events = []

#set train and test events with 75% train on 500000 events and rest is for discovery
sample_events += eventsList[0:37500]
test_events += eventsList[37500:50000]
discovery_events += eventsList[50000:]

sample_events_copy = sample_events.copy()
test_events_copy = test_events.copy()
discovery_events_copy = discovery_events.copy()

sample_SUSY = []
test_SUSY = []
discovery_SUSY = []

for i in sample_events:
  sample_SUSY.append(i[0])
  i.pop(0)

for i in test_events:
  test_SUSY.append(i[0])
  i.pop(0)

for i in discovery_events:
  discovery_SUSY.append(i[0])
  i.pop(0)

# Create and manipulate data (70% train, 30% test)
train_input = sample_events
train_label = sample_SUSY
test_input = test_events
test_label = test_SUSY
discover_input = discovery_events
discovery_label = discovery_SUSY

# Convert data to PyTorch tensors and assign to correct device
train_input = torch.tensor(train_input, dtype=torch.float64).to(device)
train_label = torch.tensor(
    train_label, dtype=torch.double).unsqueeze(1).to(device)
test_input = torch.tensor(test_input, dtype=torch.float64).to(device)
test_label = torch.tensor(
    test_label, dtype=torch.double).unsqueeze(1).to(device)
discover_input = torch.tensor(discover_input, dtype=torch.float64).to(device)
discovery_label = torch.tensor(
    discovery_label, dtype=torch.double).unsqueeze(1).to(device)

# Initialize model, specify `double` if the model expects double precision
model = KAN(width=[18, 30, 30, 1], grid=4, k=4, device=device).double()
'''
MODIFY THE WIDTH AS YOU WISH TO TRY GET AS HIGH AN ACCURACY AS POSSIBLE
'''

def train_acc():
    return (model(train_input).argmax(dim=1) == train_label).float().mean()


def test_acc():
    print((model(test_input).argmax(dim=1) == test_label).float().mean())
    return (model(test_input).argmax(dim=1) == test_label).float().mean()

# Run training with adjusted metric calculations
results = model.train({
    'train_input': train_input,
    'train_label': train_label,
    'test_input': test_input,
    'test_label': test_label
}, opt="LBFGS", steps=17, metrics=(train_acc, test_acc), loss_fn=torch.nn.MSELoss(), device=device)

'''
MODIFY THE STEPS AS YOU WISH TO TRY GET AS LOW A LOSS AS POSSIBLE
'''

def correction(x):
    if x <0.5:
        return 0
    else:
        return 1

def accuracy(model, x, y):
    result = model(x)
    correct = 0
    for i in range(len(result)):
        #print(f"Result: {correction(result[i])}, Actual: {y[i]}")
        if correction(result[i]) == y[i]:
            correct += 1
    print(correct/len(x))

y_predicted_train = model(discover_input[0:len(discover_input)]).cpu()
y_predicted_test = model(discover_input[0:len(discover_input)]).cpu()
y_predicted_discover = model(discover_input[0:len(discover_input)]).cpu()

accuracy(model, train_input, train_label)

'''
USE HERE TO TEST ACCURACY ON TRAIN AND TEST AND IF TIME ALLOWS ON DISCOVERY
AND THEN SEND THEM TO ME
'''

cumulative_events = 0 # start counter for total number of events for which output is saved
for s in processes: # loop over samples
    data_NN[s]['NN_output'] = y_predicted[cumulative_events:cumulative_events+len(data_NN[s])]
    cumulative_events += len(data_NN[s]) # increment counter for total number of events

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

def calculate_z_scores(dnn_outputs, mean_background, std_dev_background):
    """Calculates Z-scores for DNN outputs given background mean and std dev."""
    z_scores = (dnn_outputs - mean_background) / std_dev_background
    return z_scores

def plot_z_score_distribution(z_scores):
    """Plots the distribution of Z-scores and estimates significance."""
    plt.hist(z_scores, bins=30, density=True, alpha=0.6, label='Z-score Distribution')
    plt.xlabel('Z-score')
    plt.ylabel('Density')
    plt.title('Distribution of Z-scores')

    # Fit a normal distribution to the Z-scores
    mu, std = norm.fit(z_scores)
    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 100)
    p = norm.pdf(x, mu, std)
    plt.plot(x, p, 'k', linewidth=2, label='Normal Fit')
    plt.legend()

    # Estimate significance (assuming 5 sigma threshold for discovery)
    p_value = 1 - norm.cdf(5, mu, std)  # Probability of Z > 5
    significance = -norm.ppf(p_value)   # Convert p-value to sigma
    print(f"Estimated Significance of method 1: {significance:.2f} sigma")

    plt.show()

from statistics import stdev

# Example usage (replace with your actual DNN outputs)
dnn_outputs_discover = y_predicted_discover  # Simulated DNN outputs between 0 and 1

dnn_outputs_discover_list = []

for i in dnn_outputs_discover:
    dnn_outputs_discover_list.append(i.detach().numpy())

dnn_discover_background_outputs_list = []

for i in range(len(discovery_events_copy)):
    if discovery_events_copy[i][0] == 0:
        dnn_discover_background_outputs_list.append(dnn_outputs_discover_list[i])

# Assumptions based on the reference text (replace with actual values if available)
mean_background = np.average(dnn_discover_background_outputs_list)  # Mean DNN output for background events
std_dev_background = stdev(dnn_discover_background_outputs_list)  # Standard deviation of DNN output for background events

z_scores = calculate_z_scores(np.array(dnn_outputs_list), mean_background, std_dev_background)
plot_z_score_distribution(z_scores)

'''
SEND ME THIS PLOT AND THE NUMBER BELOW THE GRAPH
'''

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm, chi2

def calculate_ams(s, b):
    """Calculates Approximate Median Significance (AMS)."""
    return np.sqrt(2 * ((s + b + 10) * np.log(1 + s/(b + 10)) - s))

def likelihood_ratio_test(s, b):
    """Performs likelihood ratio test and calculates significance."""
    LR = (np.exp(-(s+b)) * (s+b)**s / np.math.factorial(s)) / (np.exp(-b) * b**s / np.math.factorial(s))
    test_statistic = -2 * np.log(LR)
    p_value = 1 - chi2.cdf(test_statistic, 1)
    significance = -norm.ppf(p_value)
    return p_value, significance

# Set data
dnn_outputs = dnn_outputs_list  # DNN outputs
true_labels = discovery_SUSY  # Simulated true labels (0: background, 1: signal)

thresholds = np.arange(0.05, 1, 0.05)  # Vary threshold from 0.05 to 0.95
ams_values = []
tprs = []
fprs = []

for threshold in thresholds:
    predicted_labels = (dnn_outputs >= threshold).astype(int)

    # True Positives, False Positives, True Negatives, False Negatives
    tp = np.sum((predicted_labels == 1) & (true_labels == 1))
    fp = np.sum((predicted_labels == 1) & (true_labels == 0))
    tn = np.sum((predicted_labels == 0) & (true_labels == 0))
    fn = np.sum((predicted_labels == 0) & (true_labels == 1))

    ams = calculate_ams(tp, fp)
    ams_values.append(ams)
    tprs.append(tp / (tp + fn))  # True Positive Rate
    fprs.append(fp / (fp + tn))  # False Positive Rate

# Find optimal threshold
optimal_threshold_index = np.argmax(ams_values)
optimal_threshold = thresholds[optimal_threshold_index]
optimal_ams = ams_values[optimal_threshold_index]

# Likelihood ratio test at optimal threshold
s = np.sum(dnn_outputs >= optimal_threshold)
b = np.sum(dnn_outputs < optimal_threshold)
p_value, significance = likelihood_ratio_test(s, b)

print(f"Optimal Threshold: {optimal_threshold:.2f}")
print(f"Optimal AMS: {optimal_ams:.2f}")
print(f"Significance at Optimal Threshold: {significance:.2f} sigma")

# Plot ROC curve
plt.plot(fprs, tprs, label=f'AUC = {np.trapz(tprs, fprs):.2f}')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve')
plt.legend(loc='lower right')
plt.show()
'''
SEND ME THIS PLOT AND THE NUMBER ABOVE THE GRAPH
'''

import numpy as np
import matplotlib.pyplot as plt

dnn_outputs_train = y_predicted_train
dnn_outputs_test = y_predicted_test

dnn_outputs_train_list = []
dnn_outputs_test_list = []

dnn_train_background_outputs_list = []
dnn_train_signal_outputs_list = []
dnn_test_background_outputs_list = []
dnn_test_signal_outputs_list = []


for i in range(len(sample_events_copy)):
    if sample_events_copy[i][32] == 'b':
        dnn_train_background_outputs_list.append(dnn_outputs_train_list[i])
    else:
        dnn_train_signal_outputs_list.append(dnn_outputs_test_list[i])

for i in range(len(test_events_copy)):
    if test_events_copy[i][32] == 'b':
        dnn_test_background_outputs_list.append(dnn_outputs_train_list[i])
    else:
        dnn_test_signal_outputs_list.append(dnn_outputs_test_list[i])

# Data for plot
np.random.seed(42)  # For reproducibility
signal_train_prob = dnn_train_signal_outputs_list
bkg_train_prob = dnn_train_background_outputs_list
signal_test_prob = dnn_test_signal_outputs_list
bkg_test_prob = dnn_test_background_outputs_list

# Calculate binned probabilities and uncertainties
bins = np.linspace(0, 1, 21)  # Define bins for the histogram
signal_train_y, _, _ = plt.hist(signal_train_prob, bins=bins, alpha=0, density=True)
bkg_train_y, _, _ = plt.hist(bkg_train_prob, bins=bins, alpha=0, density=True)

# Calculate error bars using binomial proportion confidence interval
def binom_conf_interval(p, n, z=1.96): # 95% confidence interval
    se = np.sqrt(p * (1 - p) / n)
    return z * se

signal_test_y, _, _ = plt.hist(signal_test_prob, bins=bins, alpha=0, density=True)
signal_test_yerr = binom_conf_interval(signal_test_y, len(signal_test_prob))
bkg_test_y, _, _ = plt.hist(bkg_test_prob, bins=bins, alpha=0, density=True)
bkg_test_yerr = binom_conf_interval(bkg_test_y, len(bkg_test_prob))

# Plotting
plt.figure(figsize=(10, 6))

# Histograms for training data
plt.bar(bins[:-1], signal_train_y, width=np.diff(bins), align="edge", alpha=0.7, color='red', label='S (train)')
plt.bar(bins[:-1], bkg_train_y, width=np.diff(bins), align="edge", alpha=0.7, color='blue', label='B (train)')

# Scatter plot with error bars for test data
plt.errorbar(
    (bins[:-1] + bins[1:]) / 2, signal_test_y,
    yerr=signal_test_yerr, fmt='o', color='purple', label='S (test)'
)
plt.errorbar(
    (bins[:-1] + bins[1:]) / 2, bkg_test_y,
    yerr=bkg_test_yerr, fmt='o', color='blue', label='B (test)'
)

# Formatting
plt.yscale('log')
plt.xlabel('Classifier Output (Probability of being signal)')
plt.ylabel('Density')
plt.title('Classifier Output for Signal and Background')
plt.legend()
plt.grid(alpha=0.4)

plt.show()


'''
SEND ME THIS PLOT
'''

