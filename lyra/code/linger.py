import time
import scanpy as sc
import scipy.sparse as sp
import pandas as pd
from pathlib import Path

# base path for container 
BASE = "/project/"

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")

# ---------------------------------------------------------------------------------------------------------------
# 1) Read multi-omics data

from LingerGRN.preprocess import *

start = time.time()
log("Reading input multi-omics matrix...")
adata = sc.read_10x_h5(BASE + 'data/pbmc_granulocyte_sorted_10k_filtered_feature_bc_matrix.h5', gex_only=False)
matrix = adata.X.T
adata.var['gene_ids'] = adata.var.index

features = pd.DataFrame(adata.var['gene_ids'].values.tolist(), columns=[1])
features[2] = adata.var['feature_types'].values
barcodes = pd.DataFrame(adata.obs_names, columns=[0])
label = pd.read_csv(BASE + 'data/PBMC_label.txt', sep='\t', header=0)
adata_RNA, adata_ATAC = get_adata(matrix, features, barcodes, label)
log(f"Adata loaded: {adata.shape[0]} cells, {adata.shape[1]} features")
log(f"obs sample:\n{adata.obs.head()}")
log(f"var sample:\n{adata.var.head()}")
log(f"Step completed in {time.time()-start:.1f}s\n")

# ---------------------------------------------------------------------------------------------------------------
# 2) Preprocess
start = time.time()
log("Filtering low-count cells and genes...")
sc.pp.filter_cells(adata_RNA, min_genes=200)
sc.pp.filter_genes(adata_RNA, min_cells=3)
sc.pp.filter_cells(adata_ATAC, min_genes=200)
sc.pp.filter_genes(adata_ATAC, min_cells=3)

selected_barcode = list(set(adata_RNA.obs['barcode'].values) & set(adata_ATAC.obs['barcode'].values))
barcode_idx = pd.DataFrame(range(adata_RNA.shape[0]), index=adata_RNA.obs['barcode'].values)
adata_RNA = adata_RNA[barcode_idx.loc[selected_barcode][0]]
barcode_idx = pd.DataFrame(range(adata_ATAC.shape[0]), index=adata_ATAC.obs['barcode'].values)
adata_ATAC = adata_ATAC[barcode_idx.loc[selected_barcode][0]]
log(f"Filtered RNA: {adata_RNA.shape[0]} cells, {adata_RNA.shape[1]} genes")
log(f"Filtered ATAC: {adata_ATAC.shape[0]} cells, {adata_ATAC.shape[1]} peaks")
log(f"Step completed in {time.time()-start:.1f}s\n")

# ---------------------------------------------------------------------------------------------------------------
# 3) Generate pseudo-bulk

import os
from LingerGRN.pseudo_bulk import *

start = time.time()
log("Generating pseudo-bulk / metacells...")
samplelist = list(set(adata_ATAC.obs['sample'].values))
TG_pseudobulk = pd.DataFrame([])
RE_pseudobulk = pd.DataFrame([])
singlepseudobulk = adata_RNA.obs['sample'].nunique() > 10

for tempsample in samplelist:
    adata_RNAtemp = adata_RNA[adata_RNA.obs['sample'] == tempsample]
    adata_ATACtemp = adata_ATAC[adata_ATAC.obs['sample'] == tempsample]
    TG_temp, RE_temp = pseudo_bulk(adata_RNAtemp, adata_ATACtemp, singlepseudobulk)
    TG_pseudobulk = pd.concat([TG_pseudobulk, TG_temp], axis=1)
    RE_pseudobulk = pd.concat([RE_pseudobulk, RE_temp], axis=1)
    RE_pseudobulk[RE_pseudobulk > 100] = 100

log(f"TG_pseudobulk sample:\n{TG_pseudobulk.head()}")
log(f"RE_pseudobulk sample:\n{RE_pseudobulk.head()}")
log(f"Step completed in {time.time()-start:.1f}s\n")

# ---------------------------------------------------------------------------------------------------------------
# 4) Save pseudobulk
start = time.time()
log("Saving pseudobulk data...")
os.makedirs(BASE + 'data', exist_ok=True)
adata_ATAC.write(BASE + 'data/adata_ATAC.h5ad')
adata_RNA.write(BASE + 'data/adata_RNA.h5ad')
TG_pseudobulk.fillna(0).to_csv(BASE + 'data/TG_pseudobulk.tsv')
RE_pseudobulk.fillna(0).to_csv(BASE + 'data/RE_pseudobulk.tsv')
pd.DataFrame(adata_ATAC.var['gene_ids']).to_csv(BASE + 'data/Peaks.txt', header=None, index=None)
log(f"Step completed in {time.time()-start:.1f}s\n")

# ---------------------------------------------------------------------------------------------------------------
# 5) Training the model

from LingerGRN.preprocess import *  

start = time.time()
log("Preprocessing and training LINGER model...")

Datadir = BASE + "LINGER_data/"
GRNdir = Datadir + 'data_bulk/'
outdir = BASE + "LINGER_output/"
genome = 'hg38'
method = 'LINGER'

preprocess(TG_pseudobulk, RE_pseudobulk, GRNdir, genome, method, outdir)

import LingerGRN.LINGER_tr as LINGER_tr
activef='ReLU'
LINGER_tr.training(GRNdir, method, outdir, activef, species='Human')

log(f"Step completed in {time.time()-start:.1f}s\n")

# ---------------------------------------------------------------------------------------------------------------
# 6) Generate regulatory networks

import LingerGRN.LL_net as LL_net

start = time.time()
log("Generating cell population GRNs...")
LL_net.TF_RE_binding(GRNdir, adata_RNA, adata_ATAC, genome, method, outdir=outdir)
LL_net.cis_reg(GRNdir, adata_RNA, adata_ATAC, genome, method, outdir=outdir)
LL_net.trans_reg(GRNdir, method, outdir, genome)
log("GRNs generation done")
log(f"Step completed in {time.time()-start:.1f}s\n")
