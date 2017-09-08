#!/usr/bin/env python

from __future__ import print_function

import argparse

import pandas as pd
import pylab as pl
from sklearn.decomposition import PCA
from sklearn.decomposition import RandomizedPCA
from sklearn.manifold import TSNE

import zegami_tools as zt

parser = argparse.ArgumentParser(description='''This is a script that applies 
				 unsupervised learning to a directory of images
				 and appends x and y params to be used by
				 scatterplot in Zegami.''');
parser.add_argument(
    '-i',
    '--input',
    help='Zegami input file name (should be a TSV)',
    required=True
)
parser.add_argument(
    '-b',
    '--bigwig',
    help='Input file file with bigWig plot data (should be a TSV)',
    required=True
)
parser.add_argument(
    '-n',
    '--bins',
    help='Number of bins used for the peak',
    type=int,
    required=False,
    default=100
)
parser.add_argument(
    '-s',
    '--sample',
    help='(int) Pick a number of random samples to draw from the dataset if ' \
	 'you don\'t want to use all samples. Omit this option to use the ' \
	 'entire dataset',
    type=int,
    required=False)
parser.add_argument(
    '-o',
    '--output',
    help='Output file name (will be original TSV with the X and Y columns ' \
	 'appended)',
    required=True
)
parser.add_argument(
    '-a',
    '--analysis_type',
    help='PCA or TSNE.',
    required=False,
    default="PCA"
)
parser.add_argument(
    '-p',
    '--plot',
    help='Do a plot based on resulting X and Y coords (requires PIL).',
    action='store_true',
    required=False
)
args = parser.parse_args()



zd, merge_df, labels = zt.get_plot_data(zegami_file = args.input,
					plot_file = args.bigwig,
					bins = args.bins)

if args.sample:
    zd = zd.sample(args.sample, random_state=0)
    zd.index = range(zd.shape[0])
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


print('==========================')
print('Appended x and y coordinates to {} and created {}.'.format(args.input,
								  args.output))
zd.to_csv(args.output, sep="\t", index=False)
print('==========================')

if args.plot:
	pl.scatter(df['x'], df['y'], s=4)
	pl.show()
