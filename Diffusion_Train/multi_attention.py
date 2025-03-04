import torch
from torch import nn
import torch.functional as F
import math

X = torch.randn(128, 64, 512) #Batch, Time, Dimension
print(X.shape)

d_model = 512
n_head = 8

class multi_head_attention(nn.Module):
    def __init__(self, d_model, n_head) -> None:
        super(multi_head_attention, self).__init__()

        self.n_head = n_head
        self.d_model = d_model
        self.w_q = nn.Linear(d_model, d_model)
        self.w_k = nn.Linear(d_model, d_model)
        self.w_v = nn.Linear(d_model, d_model)
        self.w_combine = nn.Linear(d_model, d_model)
        self.softmax = nn.Softmax(dim=-1)
    
    def forward(self, q, k, v):
        batch, time, dimension = q.shape
        n_d = self.d_model // self.n_head
        q, k, v = self.w_q(q), self.w_k(k), self.w_v(v)

        q = q.view(batch, time, self.n_head, n_d).permute(0, 2, 1, 3)
        k = k.view(batch, time, self.n_head, n_d).permute(0, 2, 1, 3)
        v = v.view(batch, time, self.n_head, n_d).permute(0, 2, 1, 3) #permute 维度变换，改变维度的顺序

        score = q @ k.transpose(2, 3) / math.sqrt(n_d) #@作矩阵乘法
        mask = torch.tril(torch.ones(time, time, dtype=bool)) #下三角矩阵
        score = score.masked_fill(mask==0, float("-inf")) #作Softmax时，e^-inf = 0即不考虑后面的部分
        score = self.softmax(score) @ v

        score  = score.permute(0, 2, 1, 3).contiguous().view(batch, time, dimension) #恢复query顺序，并保证在内存中的连续性

        output = self.w_combine(score)
        return output

attention = multi_head_attention(d_model, n_head)
output = attention(X, X, X)
print(output, output.shape)


