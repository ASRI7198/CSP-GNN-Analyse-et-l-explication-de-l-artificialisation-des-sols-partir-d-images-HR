import torch
import torch.nn as nn


class OrderEmbeddingLoss(nn.Module):
    """
    Max-margin loss for order embeddings:
        L = mean(E_pos) + mean(relu(margin - E_neg))
    where E(A, B) = || max(0, phi(A) - phi(B)) ||_2
    """
    def __init__(self, margin: float):
        super().__init__()
        self.margin = margin

    @staticmethod
    def order_embedding_penalty(phi_A: torch.Tensor, phi_B: torch.Tensor) -> torch.Tensor:
        diff = phi_A - phi_B
        relu_diff = torch.clamp(diff, min=0.0)
        return torch.norm(relu_diff**2, dim=1)

    def forward(self,embedding_pos_A: torch.Tensor,embedding_pos_B: torch.Tensor,embedding_neg_A: torch.Tensor,embedding_neg_B: torch.Tensor) -> torch.Tensor:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        loss_pos = self.order_embedding_penalty(embedding_pos_A, embedding_pos_B)
        neg_pen = self.order_embedding_penalty(embedding_neg_A, embedding_neg_B)
        loss_neg = torch.max(torch.tensor(0.0,device=device), self.margin - neg_pen)
        loss = torch.cat([loss_pos, loss_neg], dim=0)
        return loss.mean()
    






