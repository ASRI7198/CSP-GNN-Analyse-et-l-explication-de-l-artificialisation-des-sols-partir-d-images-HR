import sys
sys.path.append('/home/rida/GNN')

import torch
import torch.optim as optim
from torch_geometric.loader import DataLoader
from Embedding_phase.MGCN.Embedding_Loss import OrderEmbeddingLoss
import Embedding_phase.Generate_data.config as args
import matplotlib.pyplot  as plt




def train_model(model, train_dataset, val_dataset):
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    train_loader = DataLoader(train_dataset,batch_size=args.HYPERPARAMETERS['batch_size'],shuffle=True)
    val_loader = DataLoader(val_dataset,batch_size=args.HYPERPARAMETERS['batch_size'],shuffle=False)

    optimizer = optim.Adam(model.parameters(),lr=args.HYPERPARAMETERS['learning_rate'],weight_decay=args.HYPERPARAMETERS['l2_reg'])
    criterion = OrderEmbeddingLoss(margin=args.HYPERPARAMETERS['margin'])

    train_losses = []
    val_losses   = []

    best_val_loss = float('inf')
    epochs_no_improve = 0
    patience = args.HYPERPARAMETERS['patience']
    min_delta = args.HYPERPARAMETERS['min_delta']
    best_model_state = None


    for epoch in range(1, args.HYPERPARAMETERS['epochs']+1):
        model.train()
        total_train_loss = 0.0

        for data_A, data_B, labels in train_loader:
            data_A = data_A.to(device)
            data_B = data_B.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()
            emb_A = model(data_A) 
            emb_B = model(data_B) 


            pos_idx = labels == 1
            neg_idx = labels == -1

            emb_pos_A = emb_A[pos_idx]
            emb_pos_B = emb_B[pos_idx]
            emb_neg_A = emb_A[neg_idx]
            emb_neg_B = emb_B[neg_idx]

            loss = criterion(emb_pos_A, emb_pos_B, emb_neg_A, emb_neg_B)
            loss.backward()
            optimizer.step()

            total_train_loss += loss.item()

        avg_train_loss = total_train_loss / len(train_loader)
        train_losses.append(avg_train_loss)

        model.eval()
        total_val_loss = 0.0
        with torch.no_grad():
            for data_A, data_B, labels in val_loader:
                data_A = data_A.to(device)
                data_B = data_B.to(device)
                labels = labels.to(device)

                emb_A = model(data_A)
                emb_B = model(data_B)


                pos_idx = labels == 1
                neg_idx = labels == -1

                emb_pos_A = emb_A[pos_idx]
                emb_pos_B = emb_B[pos_idx]

                emb_neg_A = emb_A[neg_idx]
                emb_neg_B = emb_B[neg_idx]
                
                loss = criterion(emb_pos_A, emb_pos_B, emb_neg_A, emb_neg_B)
                total_val_loss += loss.item()

        avg_val_loss = total_val_loss / len(val_loader)
        val_losses.append(avg_val_loss)

        print(f"Epoch {epoch}/{args.HYPERPARAMETERS['epochs']} , Train Loss: {avg_train_loss:.4f}, Val Loss: {avg_val_loss:.4f}")
        epoch_plot = epoch = epoch
        if avg_val_loss < best_val_loss-min_delta:
            best_val_loss = avg_val_loss
            epochs_no_improve = 0
            best_model_state = model.state_dict()
            torch.save(best_model_state, args.MODEL_SAVE_PATH_12)
            print(f"Saved best model: {args.MODEL_SAVE_PATH_12}")
        else:
            epochs_no_improve += 1
            print(f"→ Pas d’amélioration depuis {epochs_no_improve} époque(s)")
            if epochs_no_improve >= patience:
                print(f"⏱️ Early stopping : plus d’amélioration depuis {patience} époques.")
                model.load_state_dict(best_model_state)
                epoch_plot = epoch
                break


    epochs = list(range(1, epoch_plot + 1))
    plt.figure(figsize=(8,5))
    plt.plot(epochs, train_losses, label='Train Loss')
    plt.plot(epochs, val_losses,   label='Val Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training & Validation Loss')
    plt.legend()
    plt.grid(True)
    plt.savefig(args.VIS_LOSS_TRAIN_VAL_500_12, bbox_inches='tight')
    plt.show()

    return model