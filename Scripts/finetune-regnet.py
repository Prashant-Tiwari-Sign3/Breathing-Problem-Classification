"""
Fine-tuning Script for Pneumonia Classification Model

This script fine-tunes a RegNet-based deep learning model for classifying pneumonia-related medical images.
It loads a pre-trained RegNet model with ImageNet weights and fine-tunes it on a custom dataset of medical images
for pneumonia classification. The fine-tuned model is saved to a specified file path.

The custom dataset should be prepared with metadata CSV file containing image file paths and labels. It should
also have a directory containing the actual image files.

The script performs the following steps:
1. Load the pre-trained RegNet model with ImageNet weights.
2. Prepare the custom dataset using 'CustomDataset' class from 'utils.py'.
3. Split the dataset into training, validation, and test sets.
4. Create data loaders for each split.
5. Modify the model's final fully connected layer to output the desired number of classes.
6. Define the loss function and optimizer.
7. Train the model using the 'TrainLoop' class from 'utils.py'.
8. Save the fine-tuned model to a specified file path.

Usage:
    Run this script to start the fine-tuning process.
"""
import pandas as pd
from torch import save
from torch.optim import AdamW
from torch.utils.data import DataLoader
from torch.nn import Linear, BCEWithLogitsLoss
from torch.optim.lr_scheduler import MultiplicativeLR
from torchvision.models.regnet import regnet_y_3_2gf, RegNet_Y_3_2GF_Weights

import sys
sys.path.append("C:\College\Projects\Breathing-Problem-Classification")
from utils import ImagesOnlyDataset, train_loop

import warnings
warnings.filterwarnings("ignore")

def finetune():
    weights = RegNet_Y_3_2GF_Weights.IMAGENET1K_V2
    model = regnet_y_3_2gf(weights=weights)

    train_targets = pd.read_csv("Data/Processed/train_targets.csv")
    train_features = pd.read_csv("Data/Processed/train_features.csv")
    val_targets = pd.read_csv("Data/Processed/val_targets.csv")
    val_features = pd.read_csv("Data/Processed/val_features.csv")

    train_dataset = ImagesOnlyDataset(train_features['filename'], train_targets, "Data/images", 232, 224)
    val_dataset = ImagesOnlyDataset(val_features['filename'], val_targets, "Data/images", 232, 224, False)
    
    train_loader = DataLoader(train_dataset, 32, shuffle=True)
    val_loader = DataLoader(val_dataset, 32, shuffle=True)

    num_classes = 22
    in_features = model.fc.in_features
    model.fc = Linear(in_features, num_classes)
    def lr_lambda(epoch):
        if epoch <= 20:
            return 0.9
        return 1
    criterion = BCEWithLogitsLoss()
    optimizer = AdamW(model.parameters(), lr=0.001)
    scheduler = MultiplicativeLR(optimizer, lr_lambda)

    train_loop(model, optimizer, criterion, train_loader, val_loader, scheduler, "Data/Performance/RegNet.png", 100, 5, 15, True, 'cuda')

    model_path = 'Models/FinetunedRegNet.pth'

    save(model.state_dict(), model_path)

if __name__ == '__main__':
    finetune()