
import sys
import os
import random
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np
import json

# Ensure backend modules are available
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from simulate_auc_benchmark import generate_student_data, MockBKT

# --- 1. GAT LAYER DEFINITION ---
class GATLayer(nn.Module):
    def __init__(self, in_features, out_features, dropout, alpha, concat=True):
        super(GATLayer, self).__init__()
        self.dropout = dropout
        self.in_features = in_features
        self.out_features = out_features
        self.alpha = alpha
        self.concat = concat

        self.W = nn.Parameter(torch.zeros(size=(in_features, out_features)))
        nn.init.xavier_uniform_(self.W.data, gain=1.414)
        self.a = nn.Parameter(torch.zeros(size=(2*out_features, 1)))
        nn.init.xavier_uniform_(self.a.data, gain=1.414)

        self.leakyrelu = nn.LeakyReLU(self.alpha)

    def forward(self, input, adj):
        h = torch.mm(input, self.W)
        N = h.size()[0]

        a_input = torch.cat([h.repeat(1, N).view(N * N, -1), h.repeat(N, 1)], dim=1).view(N, -1, 2 * self.out_features)
        e = self.leakyrelu(torch.matmul(a_input, self.a).squeeze(2))

        zero_vec = -9e15*torch.ones_like(e)
        attention = torch.where(adj > 0, e, zero_vec)
        attention = F.softmax(attention, dim=1)
        attention = F.dropout(attention, self.dropout, training=self.training)
        h_prime = torch.matmul(attention, h)

        if self.concat:
            return F.elu(h_prime)
        else:
            return h_prime

class MGKT_GNN(nn.Module):
    def __init__(self, nfeat, nhid, nclass, dropout, alpha, nheads):
        super(MGKT_GNN, self).__init__()
        self.dropout = dropout

        self.attentions = [GATLayer(nfeat, nhid, dropout=dropout, alpha=alpha, concat=True) for _ in range(nheads)]
        for i, attention in enumerate(self.attentions):
            self.add_module('attention_{}'.format(i), attention)

        self.out_att = GATLayer(nhid * nheads, nclass, dropout=dropout, alpha=alpha, concat=False)

    def forward(self, x, adj):
        x = F.dropout(x, self.dropout, training=self.training)
        x = torch.cat([att(x, adj) for att in self.attentions], dim=1)
        x = F.dropout(x, self.dropout, training=self.training)
        x = F.sigmoid(self.out_att(x, adj))
        return x

# --- 2. PREPARING GRAPH DATA ---
# We define a 4-node graph: Basics -> Loops -> Recursion, and Debugging (connected to Loops/Recursion)
def get_knowledge_graph():
    # 0: Basics, 1: Loops, 2: Recursion, 3: Debugging
    adj = torch.tensor([
        [1, 1, 0, 0], # Basics connects to self and Loops
        [0, 1, 1, 1], # Loops connects to self, Recursion, and Debugging
        [0, 0, 1, 1], # Recursion connects to self and Debugging
        [0, 0, 0, 1]  # Debugging connects to self
    ], dtype=torch.float32)
    return adj

# --- 3. TRAINING LOOP ---
def train():
    print("Initializing GAT Training for MGKT...")
    
    # Hyperparams
    n_students = 1000
    n_steps = 20
    lr = 0.005
    epochs = 40
    
    # Model: 3 input features (Tutor, Code, Debug), 8 hidden, 1 output (Mastery)
    model = MGKT_GNN(nfeat=3, nhid=8, nclass=1, dropout=0.2, alpha=0.2, nheads=2)
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=5e-4)
    adj = get_knowledge_graph()
    
    # Data Generation
    print("Generating synthetic student data...")
    dataset = generate_student_data(n_students, n_steps)
    
    # We simplify training by treating each node's mastery as a separate prediction task
    # In reality, MGKT predicts success probability of the next interaction.
    
    model.train()
    for epoch in range(epochs):
        optimizer.zero_grad()
        total_loss = 0
        
        # We sample a subset of students per epoch for performance
        batch = random.sample(dataset, 50)
        
        for history in batch:
            # We simulate the BKT state progression
            bkt_states = torch.tensor([[0.1, 0.1, 0.1]] * 4, dtype=torch.float32) # Initial [T, C, D] for 4 nodes
            
            for step_data in history:
                source, is_correct, _ = step_data
                
                # Forward pass: Aggregate current states via GAT
                # Prediction for the 'current' concept being worked on
                # For training simplicity, we assume nodes map to steps: 
                # steps 1-5 -> Node 0, 6-10 -> Node 1, 11-15 -> Node 2, 16-20 -> Node 3
                node_idx = 0 if len(history) < 5 else (1 if len(history) < 10 else (2 if len(history) < 15 else 3))
                
                preds = model(bkt_states, adj)
                target = torch.tensor([1.0 if is_correct else 0.0], dtype=torch.float32)
                
                loss = F.binary_cross_entropy(preds[node_idx], target)
                loss.backward()
                total_loss += loss.item()
                
                # Update latent BKT states (Simplified simulation)
                src_map = {"tutor": 0, "code": 1, "debug": 2}
                col = src_map.get(source, 0)
                if is_correct:
                    bkt_states[node_idx, col] = min(0.95, bkt_states[node_idx, col] + 0.2)
                else:
                    bkt_states[node_idx, col] = max(0.05, bkt_states[node_idx, col] - 0.1)

        optimizer.step()
        if epoch % 5 == 0:
            print(f"Epoch {epoch:2d} | Loss: {total_loss:.4f}")

    # Save weights
    print("Training complete. Saving GAT model state...")
    torch.save(model.state_dict(), "backend/mgkt_gat_model.bin")
    
    # Export specific attention weights for mock usage if needed
    # But usually, it's better to just use the model for inference.
    print("GNN Training Artifacts saved to backend/mgkt_gat_model.bin")

if __name__ == "__main__":
    train()
