import os
import sys
import torch
import numpy as np
import pandas as pd
import scipy
import sklearn

print("="*60)
print("LINGER Environment Test")
print("="*60)

# -------------------------
# Python info
# -------------------------
print("Python:", sys.version)
print("Executable:", sys.executable)

# -------------------------
# PyTorch info
# -------------------------
print("\n--- PyTorch ---")
print("Torch version:", torch.__version__)
print("CUDA compiled:", torch.version.cuda)
print("CUDA available:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("GPU count:", torch.cuda.device_count())
    print("GPU name:", torch.cuda.get_device_name(0))
else:
    print("WARNING: No GPU detected")

# -------------------------
# CUDA test
# -------------------------
print("\n--- CUDA Tensor Test ---")

try:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    x = torch.randn(2000, 2000, device=device)
    y = torch.randn(2000, 2000, device=device)

    z = torch.matmul(x, y)

    print("Tensor test OK on", device)

except Exception as e:
    print("CUDA test FAILED")
    print(e)

# -------------------------
# NN test (similar to your Net)
# -------------------------
print("\n--- Neural Network Test ---")

class Net(torch.nn.Module):
    def __init__(self, input_size):
        super().__init__()
        self.fc1 = torch.nn.Linear(input_size, 64)
        self.fc2 = torch.nn.Linear(64, 16)
        self.fc3 = torch.nn.Linear(16, 1)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)


try:
    model = Net(128).to(device)

    data = torch.randn(100, 128, device=device)
    target = torch.randn(100, 1, device=device)

    opt = torch.optim.Adam(model.parameters(), lr=1e-3)

    out = model(data)
    loss = torch.mean((out - target)**2)

    loss.backward()
    opt.step()

    print("NN forward/backward OK")

except Exception as e:
    print("NN test FAILED")
    print(e)

# -------------------------
# SciPy / Sparse test
# -------------------------
print("\n--- SciPy Sparse Test ---")

from scipy.sparse import coo_matrix

try:
    row = np.array([0, 1, 2])
    col = np.array([1, 2, 0])
    data = np.array([3.0, 4.0, 5.0])

    mat = coo_matrix((data, (row, col)), shape=(3,3))
    dense = mat.toarray()

    print("Sparse matrix OK")

except Exception as e:
    print("Sparse test FAILED")
    print(e)

# -------------------------
# Torch save/load test
# -------------------------
print("\n--- torch.load() Test ---")

try:
    tmpfile = "test_model.pt"

    torch.save(model, tmpfile)
    m2 = torch.load(tmpfile, map_location=device)

    out2 = m2(data)

    os.remove(tmpfile)

    print("torch.save/load OK")

except Exception as e:
    print("torch.load FAILED")
    print(e)

# -------------------------
# Memory test (important for your code)
# -------------------------
print("\n--- Memory Test ---")

try:
    big = np.random.randn(5000, 5000)
    big2 = big @ big.T

    print("Large matrix multiply OK (~200MB)")

except Exception as e:
    print("Memory test FAILED")
    print(e)

# -------------------------
# Final status
# -------------------------
print("\n==============================")
print("Environment test COMPLETE")
print("==============================")
