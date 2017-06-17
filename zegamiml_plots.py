#!/usr/bin/env python

from __future__ import print_function
import argparse

parser = argparse.ArgumentParser(description="This is a script that applies unsupervised learning to a directory of images and appends x and y params to be used by scatterplot in Zegami.");
parser.add_argument('-i','--input', help='Zegami input file name (should be a TSV)',required=True)
parser.add_argument('-c','--columns', type=int, help='Number of columns in zegami input file',required=True)
parser.add_argument('-b','--bigwig', help='Input file file with bigWig plot data (should be a TSV)',required=True)
parser.add_argument('-s','--sample', help='Pick a number of random samples to draw from the dataset if you don\'t want to use all samples',required=False)
parser.add_argument('-o','--output', help='Output file name (will be original TSV with the X and Y columns appended',required=True)
parser.add_argument('-a','--analysis_type', help='PCA or TSNE.',required=False, default="PCA")
parser.add_argument('-p','--plot', help='Do a plot based on resulting X and Y coords (requires PIL).',action='store_true', required=False)
args = parser.parse_args()

import pandas as pd
import pylab as pl
import zegami_tools as zt
from sklearn.decomposition import PCA
from sklearn.decomposition import RandomizedPCA
from sklearn.manifold import TSNE

zd, merge_df = zt.get_plot_data(zegami_file = args.input,
				plot_file = args.bigwig,
				col_num = args.columns)

if args.sample:
    zd = zd.sample(args.sample, random_state=0)
    merge_df = merge_df.sample(args.sample, random_state=0)
data = merge_df.iloc[:,1:].values

print("Creating PCA or TSNE...")
if (args.analysis_type == "TSNE"): 
	pca = TSNE(random_state=0)
else:
	pca = PCA(svd_solver='randomized', n_components=2)

X = pca.fit_transform(data)
df = pd.DataFrame({"x": X[:, 0], "y": X[:, 1]})

x_label =  args.analysis_type + "_x"
y_label =  args.analysis_type + "_y"

zd[x_label]=df['x']
zd[y_label]=df['y']


print("==========================")
print("Appended x and y coordinates to "+args.input+" and created "+args.output+".")
zd.to_csv(args.output,sep="\t",index=False)
print("==========================")

if args.plot:
	pl.scatter(df['x'], df['y'], s=4)
	pl.show()
