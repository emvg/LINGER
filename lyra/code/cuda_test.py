import os
import sys
import time
import tempfile

def log(msg):
    print(f"[TEST] {msg}", flush=True)

log("Starting LINGER environment test")

# --------------------------------------------------
# 1. Python info
# --------------------------------------------------
log(f"Python executable: {sys.executable}")
log(f"Python version: {sys.version}")

# --------------------------------------------------
# 2. PyTorch check
# --------------------------------------------------
try:
    import torch
    log(f"PyTorch version: {torch.__version__}")
except Exception as e:
    log("ERROR: Cannot import torch")
    raise e


# --------------------------------------------------
# 3. CUDA / GPU check
# --------------------------------------------------
log(f"CUDA available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    try:
        log(f"CUDA device count: {torch.cuda.device_count()}")
        log(f"Current device: {torch.cuda.current_device()}")
        log(f"Device name: {torch.cuda.get_device_name(0)}")
    except Exception as e:
        log("WARNING: CUDA detected but device info failed")
        log(str(e))
else:
    log("WARNING: No GPU detected (running CPU mode)")


# --------------------------------------------------
# 4. torch.load compatibility test
# --------------------------------------------------
log("Testing torch.save / torch.load...")

tmp_dir = tempfile.mkdtemp()
test_file = os.path.join(tmp_dir, "test_model.pt")

dummy = {
    "tensor": torch.randn(5, 5),
    "number": 42
}

torch.save(dummy, test_file)

try:
    loaded = torch.load(test_file)
    log("torch.load works (no weights_only error)")
except Exception as e:
    log("ERROR: torch.load failed")
    raise e


# --------------------------------------------------
# 5. LINGER import test
# --------------------------------------------------
log("Testing LingerGRN imports...")

try:
    import LingerGRN
    import LingerGRN.preprocess
    import LingerGRN.LINGER_tr
    import LingerGRN.LL_net
    log("LINGER modules imported successfully")
except Exception as e:
    log("ERROR: LINGER import failed")
    raise e


# --------------------------------------------------
# 6. Scanpy / dependencies test
# --------------------------------------------------
log("Testing scientific dependencies...")

try:
    import scanpy as sc
    import pandas as pd
    import scipy
    import numpy as np

    log(f"scanpy: {sc.__version__}")
    log(f"pandas: {pd.__version__}")
    log(f"scipy: {scipy.__version__}")
    log(f"numpy: {np.__version__}")

except Exception as e:
    log("ERROR: Scientific stack broken")
    raise e


# --------------------------------------------------
# 7. File write test (important on HPC)
# --------------------------------------------------
log("Testing filesystem write permissions...")

try:
    test_out = os.path.join(tmp_dir, "write_test.txt")
    with open(test_out, "w") as f:
        f.write("LINGER TEST OK\n")

    log("Write permission: OK")

except Exception as e:
    log("ERROR: Cannot write files")
    raise e


# --------------------------------------------------
# 8. Small GPU compute test (if available)
# --------------------------------------------------
if torch.cuda.is_available():
    log("Running small GPU compute test...")

    try:
        x = torch.randn(1000, 1000, device="cuda")
        y = torch.mm(x, x)
        torch.cuda.synchronize()

        log("GPU compute: OK")

    except Exception as e:
        log("ERROR: GPU compute failed")
        raise e


# --------------------------------------------------
# DONE
# --------------------------------------------------
log("====================================")
log("ALL TESTS PASSED ✅")
log("LINGER ENVIRONMENT IS READY")
log("====================================")
