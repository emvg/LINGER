import scanpy as sc
import os
import scipy.sparse as sp
import pandas as pd
import torch
from pathlib import Path


## pytorch

if torch.cuda.is_available():
    print("gpu enabled: YES")
    print("gpu:", torch.cuda.get_device_name(0))
else:
    print("gpu enabled: NO")




BASE = "/project/"

cwd = os.getcwd()
print("Current working directory:", cwd)

file_path = [ 
    Path(BASE + "data/"),
    Path(BASE + "LINGER_data/"),
    Path(BASE + "LINGER_output/") 
]

for fp in file_path:
    if fp.exists():
        print(f"File exists: {fp}")
    else:
        print(f"File NOT found: {fp}")
