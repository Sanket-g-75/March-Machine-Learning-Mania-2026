# Will be building a Encoder only model to train. 

'''
Steps

Team Features -> Transformer Encoder -> Transformer Embeddings -> Form z using Embeddings -> MLP(z) -> Sigmoid() -> Probability
'''

import pandas as pd
import numpy as np
import os
import math

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset
from torch.utils.data import DataLoader

import warnings
warnings.filterwarnings('ignore')



# Get the team dataset
class TeamDataset(Dataset):
    def __init__(self, data):
        self.data = torch.tensor(data.values, dtype=torch.float32)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]
    

class TeamEncoder(nn.Module):
    def __init__(self, input_dim, d_model=128, n_heads=4, n_layers=2):
        super().__init__()

        # Project stats → embedding
        self.input_proj = nn.Linear(input_dim, d_model)

        # CLS token
        self.cls = nn.Parameter(torch.randn(1, 1, d_model))

        # Transformer Encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=n_heads,
            dim_feedforward=256,
            batch_first=True
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)

        # Decoder (for reconstruction)
        self.decoder = nn.Sequential(
            nn.Linear(d_model, 128),
            nn.ReLU(),
            nn.Linear(128, input_dim)
        )

    def forward(self, x):
        # x: (B, input_dim)

        B = x.size(0)

        x = self.input_proj(x)              # (B, d_model)
        x = x.unsqueeze(1)                 # (B, 1, d_model)

        cls = self.cls.expand(B, 1, -1)    # (B, 1, d_model)

        x = torch.cat([cls, x], dim=1)     # (B, 2, d_model)

        x = self.encoder(x)                # (B, 2, d_model)

        cls_out = x[:, 0, :]               # (B, d_model)

        recon = self.decoder(cls_out)      # (B, input_dim)

        return recon, cls_out
    

def train_encoder(model, dataloader, epochs=20, lr=1e-3):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()

    for epoch in range(epochs):
        total_loss = 0

        for batch in dataloader:
            x = batch.to(device)  # (B, input_dim)

            recon, _ = model(x)

            loss = criterion(recon, x)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        print(f"Epoch {epoch+1}, Loss: {total_loss:.4f}")




class MatchPredictor(nn.Module):
    def __init__(self, encoder, d_model):
        super().__init__()

        self.encoder = encoder

        self.classifier = nn.Sequential(
            nn.Linear(d_model * 4, 128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )

    def forward(self, teamA, teamB):
        _, zA = self.encoder(teamA)   # (B, d)
        _, zB = self.encoder(teamB)

        x = torch.cat([
            zA - zB,
            zA * zB,
            zA,
            zB
        ], dim=-1)

        return torch.sigmoid(self.classifier(x))
    





class MatchDatasetEmb(Dataset):
    def __init__(self, match_data, embedding_matrix):
        """
        match_data: list of (teamA_id, teamB_id, label)
        embedding_matrix: tensor (num_teams, d_model)
        """
        self.matches = match_data
        self.emb = embedding_matrix

    def __len__(self):
        return len(self.matches)

    def __getitem__(self, idx):
        row = self.matches.iloc[idx]
        teamA_id = row["TeamAID"]
        teamB_id = row["TeamBID"]
        label = row["Win"]

        # match team embeddings based on their keys
        teamA = team_ids.index(teamA_id)
        teamB = team_ids.index(teamB_id)

        zA = self.emb[teamA]
        zB = self.emb[teamB]

        return zA, zB, torch.tensor(label, dtype=torch.float32)
    

class MatchPredictorEmb(nn.Module):
    def __init__(self, d_model):
        super().__init__()

        self.classifier = nn.Sequential(
            nn.Linear(d_model * 4, 128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )

    def forward(self, zA, zB):
        x = torch.cat([
            zA - zB,
            zA * zB,
            zA,
            zB
        ], dim=-1)

        return self.classifier(x)  # logits
    
# Final Classifier/ Predictor
def train_classifier(model, dataloader, epochs=10, lr=1e-3):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.BCEWithLogitsLoss()

    for epoch in range(epochs):
        model.train()
        total_loss = 0

        for zA, zB, y in dataloader:
            zA = zA.to(device)
            zB = zB.to(device)
            y = y.to(device)

            logits = model(zA, zB).squeeze()
            loss = criterion(logits, y)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        print(f"Epoch {epoch+1}/{epochs} | Loss: {total_loss/len(dataloader):.4f}")


def predict(model, teamA_id, teamB_id, embedding_matrix):
    device = next(model.parameters()).device

    teamA = team_ids.index(teamA_id)
    teamB = team_ids.index(teamB_id)

    
    zA = embedding_matrix[teamA].unsqueeze(0).to(device)
    zB = embedding_matrix[teamB].unsqueeze(0).to(device)

    model.eval()
    with torch.no_grad():
        logits = model(zA, zB)
        prob = torch.sigmoid(logits)

    return prob.item()