import sys
sys.path.append('/home/rida/GNN')

import torch
from torch_geometric.loader import DataLoader
from Embedding_phase.MGCN.Embedding_Loss import OrderEmbeddingLoss
from Embedding_phase.Generate_data.config import HYPERPARAMETERS


def test_model(model, test_dataset):

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    model.eval()

    test_loader = DataLoader(test_dataset,batch_size=HYPERPARAMETERS['batch_size'],shuffle=False)

    total_test_loss = 0.0
    criterion = OrderEmbeddingLoss(margin=HYPERPARAMETERS['margin'])


    with torch.no_grad():
        for data_A, data_B, labels in test_loader:
            data_A = data_A.to(device)
            data_B = data_B.to(device)
            labels = labels.to(device)

            h_A = model(data_A)
            h_B = model(data_B)

            pos_idx = labels == 1
            neg_idx = labels == -1

            emb_pos_A = h_A[pos_idx]
            emb_pos_B = h_B[pos_idx]

            emb_neg_A = h_A[neg_idx]
            emb_neg_B = h_B[neg_idx]

            loss = criterion(emb_pos_A, emb_pos_B, emb_neg_A, emb_neg_B)
            total_test_loss += loss.item()

    avg_test_loss = total_test_loss / len(test_loader)
    print(f"Test Loss: {avg_test_loss:.4f}")