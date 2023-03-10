# -*- coding: utf-8 -*-
"""Directions01_Swin-tiny

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1YShgL_bMM-xNw8VC7_un8wH5lNQnPEx2
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder
from torchvision.transforms import transforms
from google.colab import drive
import timm
from sklearn.metrics import roc_auc_score
import numpy as np

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Mount Google Drive
drive.mount('/content/drive')

# Define data transforms
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.5], [0.5])
])

# Load training data
train_data = ImageFolder(root='/content/drive/My Drive/Liang/Directions01/train', transform=transform)
train_loader = DataLoader(train_data, batch_size=64, shuffle=True)

# Load test data
test_data = ImageFolder(root='/content/drive/My Drive/Liang/Directions01/test', transform=transform)
test_loader = DataLoader(test_data, batch_size=64, shuffle=False)

model = timm.create_model('swin_tiny_patch4_window7_224', pretrained=True)
num_features = model.head.in_features
model.head = nn.Linear(num_features, 4)
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

y_true = []
y_scores = []

with torch.no_grad():
    for inputs, labels in test_loader:
        inputs, labels = inputs.to(device), labels.to(device)
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        test_loss += loss.item() * inputs.size(0)
        _, preds = torch.max(outputs, 1)
        test_correct += torch.sum(preds == labels.data)
        y_true += labels.cpu().numpy().tolist()
        y_scores += nn.functional.softmax(outputs, dim=1).cpu().numpy().tolist()

test_loss = test_loss / len(test_data)
test_acc = test_correct.double() / len(test_data)

print(f"Test Loss: {test_loss:.4f}, Test Acc: {test_acc:.4f}")

# Compute AUC score for each class
auc_scores = []
for i in range(4):
    auc_scores.append(roc_auc_score(np.array(y_true) == i, np.array(y_scores)[:, i]))
    print(f"AUC for class {i}: {auc_scores[-1]:.4f}")
    
# Compute mean AUC score
mean_auc = np.mean(auc_scores)
print(f"Mean AUC score: {mean_auc:.4f}")

# Compute accuracy percentage
accuracy = test_correct.double() / len(test_data) * 100

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

print(f"Test Loss: {test_loss:.4f}, Test Acc: {test_acc*100:.2f}%")