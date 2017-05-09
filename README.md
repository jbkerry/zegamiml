# zegamiml

This tool generates new columns in a tab delimited output file based on doing unsupervised machine learning using the scikit-learn package.

```
usage: zegamiml.py [-h] -i INPUT -o OUTPUT -c IMAGE_COLUMN -d IMAGE_DIR [-a ANALYSIS_TYPE] [-p]

This is a script that applies unsupervised learning to a directory of images
and appends x and y params to be used by scatterplot in Zegami.

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input file name (should be a TSV)
  -o OUTPUT, --output OUTPUT
                        Output file name (will be original TSV with the X and
                        Y columns appended
  -c IMAGE_COLUMN, --image_column IMAGE_COLUMN
                        Column name in TSV that contains the image name
  -d IMAGE_DIR, --image_dir IMAGE_DIR
                        Directory that contains all the images.
  -a ANALYSIS_TYPE, --analysis_type ANALYSIS_TYPE
                        PCA or TSNE.
  -p, --plot            Do a plot based on resulting X and Y coords (requires
                        PIL).

e.g.

python zegamiml.py -i /t1-data/user/staylor/zegami/mig_test_1/zegami.tab  -o /t1-data/user/staylor/zegami/mig_test_1/zegami_pca_tsne.tab -d /t1-data/user/staylor/zegami/mig_test_1/out/ -c path  -a TSNE -p
```

Requires Python 2.7+
