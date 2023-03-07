# -*- coding: utf-8 -*-
"""Directions01_Resnet-18

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1we22rCA7eCKR0SEgCGOvbPGsv4ZTrLaq
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.models as models
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder
from torchvision.transforms import transforms
from google.colab import drive

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# Mount Google Drive
drive.mount('/content/drive')

# Define data transforms
transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
    transforms.Normalize([0.5], [0.5])
])

# Load training data
train_data = ImageFolder(root='/content/drive/My Drive/Liang/Directions01/train', transform=transform)
train_loader = DataLoader(train_data, batch_size=64, shuffle=True)

# Load test data
test_data = ImageFolder(root='/content/drive/My Drive/Liang/Directions01/test', transform=transform)
test_loader = DataLoader(test_data, batch_size=64, shuffle=False)


model = models.resnet18(pretrained=True)
num_features = model.fc.in_features
model.fc = nn.Linear(num_features, 4)
model.to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

num_epochs = 10

for epoch in range(num_epochs):
    train_loss = 0
    train_correct = 0
    model.train()

    for inputs, labels in train_loader:
        inputs, labels = inputs.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        train_loss += loss.item() * inputs.size(0)
        _, preds = torch.max(outputs, 1)
        train_correct += torch.sum(preds == labels.data)

    train_loss = train_loss / len(train_data)
    train_acc = train_correct.double() / len(train_data)

    print(f"Epoch {epoch+1}/{num_epochs}, Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}")


test_loss = 0
test_correct = 0
model.eval()

with torch.no_grad():
    for inputs, labels in test_loader:
        inputs, labels = inputs.to(device), labels.to(device)
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        test_loss += loss.item() * inputs.size(0)
        _, preds = torch.max(outputs, 1)
        test_correct += torch.sum(preds == labels.data)

test_loss = test_loss / len(test_data)
test_acc = test_correct.double() / len(test_data)

print(f"Test Loss: {test_loss:.4f}, Test Acc: {test_acc:.4f}")




torch.save(model.state_dict(), 'resnet18_directions.pt')

from sklearn.metrics import roc_auc_score
import numpy as np

test_loss = 0
test_correct = 0
y_true = []
y_scores = []

model.eval()

with torch.no_grad():
    for inputs, labels in test_loader:
        inputs, labels = inputs.to(device), labels.to(device)
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        test_loss += loss.item() * inputs.size(0)
        _, preds = torch.max(outputs, 1)
        test_correct += torch.sum(preds == labels.data)

        # Convert labels to one-hot encoding
        labels_onehot = torch.zeros(labels.size(0), 4).to(device)
        labels_onehot.scatter_(1, labels.view(-1,1), 1)
        y_true.append(labels_onehot.cpu().numpy())

        # Softmax outputs and extract probabilities for each class
        outputs = nn.functional.softmax(outputs, dim=1)
        y_scores.append(outputs.cpu().numpy())

test_loss = test_loss / len(test_data)
test_acc = test_correct.double() / len(test_data)

y_true = np.concatenate(y_true)
y_scores = np.concatenate(y_scores)

# Calculate AUCs for each class
auc_up = roc_auc_score(y_true[:, 0], y_scores[:, 0])
auc_down = roc_auc_score(y_true[:, 1], y_scores[:, 1])
auc_left = roc_auc_score(y_true[:, 2], y_scores[:, 2])
auc_right = roc_auc_score(y_true[:, 3], y_scores[:, 3])

# Calculate mean AUC
mean_auc = (auc_up + auc_down + auc_left + auc_right) / 4

print(f"Test Loss: {test_loss:.4f}, Test Acc: {test_acc:.4f}")
print(f"AUC (Up): {auc_up:.4f}")
print(f"AUC (Down): {auc_down:.4f}")
print(f"AUC (Left): {auc_left:.4f}")
print(f"AUC (Right): {auc_right:.4f}")
print(f"Mean AUC: {mean_auc:.4f}")

test_correct = 0
model.eval()

with torch.no_grad():
    for inputs, labels in test_loader:
        inputs, labels = inputs.to(device), labels.to(device)
        outputs = model(inputs)
        _, preds = torch.max(outputs, 1)
        test_correct += torch.sum(preds == labels.data)

test_acc = test_correct.double() / len(test_data) * 100
print(f"Test Accuracy: {test_acc:.2f}%")