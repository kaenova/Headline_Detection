from torch import Tensor
from typing import Optional

# Loss metrics that supports MetricsContainer
def loss_metrics(loss: Tensor, target: Optional[Tensor] = None):
    return loss
