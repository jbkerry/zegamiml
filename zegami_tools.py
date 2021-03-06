#!/usr/bin/env python

import os
import pickle

import pandas as pd
import numpy as np

def reset():
    '''Starts a new data-frame or can be used to reset
    a filled data-frame
    
    Returns
    -------
    new_df: empty data-frame with Zegami headers as columns
    
    '''
    
    new_df = pd.DataFrame(columns = ['feature_id', 'image', 'chr',
                'bp start', 'bp end', 'FDR',
                'fold_enrichment', 'negLog10Pvalue',
                'num_tags', 'peak_length', 'summit',
                'TSNE_JK_x', 'TSNE_JK_y', 'Tags', 'plot_name',
                'peak_type', 'position'])
    
    return new_df

def append_group(df, table, name, peak_type, position):
    '''Append and import sub data-frame to the main data-frame
    
    Parameters
    ----------
    df: the pandas data-frame to append new rows to
    table: tab-delimited output from zegami
    name: name of this plot
    peak_type: are the peaks low, high, absent etc.
    position: location on TSNE plot
    
    Returns
    -------
    update_df: updated data-frame consisting of original plus the new
        data-frame
    
    '''
    
    temp_df = pd.read_csv(table, sep='\t', header=0)
    temp_df['plot_name'] = name
    temp_df['peak_type'] = peak_type
    temp_df['position'] = position
    update_df = df.append(temp_df, ignore_index=True)
    
    return update_df

def get_plot_data(zegami_file, plot_file, bins=100):
    '''Merges peaks in a zegami output dataframe with plot data from a
    text file with bigWig values in bins across the peak
    
    Parameters
    ----------
    zegami_file : str
        Path to Zegami info TSV file with the required peak IDs
    plot_file : str
        Path to a tab-delimited file with values for all peaks, split
        into bins (output from deepTools computeMatrix)
    bins : int, optional
        Number of bins that the plot has been divided into, default=100
        
    Returns
    -------
    zegami_df : pandas dataframe
        Contains data from the original Zegami input file
    merge_df : pandas dataframe 
        Contains the bins with bigWig plot data from `plot_file` and
        the corresponding peak `feature_id`
    labels : pandas Series
        If a Tags column exists in the Zegami table, the values will be
        stored in this Series for downstream machine learning
        
    '''
    
    data_df = pd.read_csv(plot_file, sep='\t',skiprows=1, header=None)
    data_df = data_df.fillna(0)
    data_df.insert(0, 'feature_id', data_df[0]+"_"+data_df[1].map(str)+"_"+data_df[2].map(str))
    data_df = data_df.drop_duplicates(subset='feature_id', keep='first')
    
    zegami_df = pd.read_csv(zegami_file, sep="\t", header=0)
    zegami_df = zegami_df.drop_duplicates(subset='feature_id', keep='first')
    zegami_df.index = range(zegami_df.shape[0])
    
    
    try:
        #labels = np.where(zegami_df['Tags']=='peak', 1, 0)
        labels = zegami_df['Tags']
    except KeyError:
        labels = ''
    
    merge_df = pd.merge(zegami_df, data_df, on='feature_id')                                  
    feature_id = merge_df['feature_id']
    merge_df = merge_df.iloc[:, -bins:]
    merge_df.insert(0, 'feature_id', feature_id)
    
    if not zegami_df['feature_id'].equals(merge_df['feature_id']):
        print('Caution: original zegami data-frame and merged data-frame are' \
              ' not in the same order')
    
    return zegami_df, merge_df, labels

def export_ML_data(data, labels, samples):
    """Splits data and labels by at position number given by `samples`.
    Outputs as a pickled dictionary called `train_test_data.p`
    
    """
    
    train_data = data[:samples]
    train_cl = labels[:samples]
    test_data = data[samples:]
    test_cl = labels[samples:]
    
    to_export = {}
    to_export['train_data'] = train_data
    to_export['train_cl'] = train_cl
    to_export['test_data'] = test_data
    to_export['test_cl'] = test_cl
    
    pickle.dump(to_export, open('train_test_data.p', 'wb'))


def get_labels(df, plot_file, dd=True):
    '''Merges peaks in a zegami output dataframe with
    plot data from a text file with bigWig values in
    100 bins across the peak
    
    Parameters
    ----------
    df: the zegami info data-frames with the required
        peak IDs
    plot_file: a tab-delimited file with values for
        all peaks, split into 100 bins
    dd: boolean, drop duplicates in the merged data-frame,
        default = True
        
    Returns
    -------
    data: a 2-dimensional numpy array containing the
        values for each peak from the zegami data-frame
        for use in TSNE
    '''
    
    _data_df = pd.read_csv(plot_file,sep='\t',skiprows=1,header=None)
    _data_df = _data_df.fillna(0)
    _data_df.insert(0, 'feature_id', _data_df[0]+"_"+_data_df[1].map(str)+"_"+_data_df[2].map(str))
    _data_df = _data_df.drop_duplicates(subset='feature_id', keep='first')
    
    #_zegami_df = pd.read_csv(df,sep="\t")
    _zegami_df = df
    
    _merge_df = pd.merge(_zegami_df, _data_df, on='feature_id')
    if dd:
        _merge_df = _merge_df.drop_duplicates(subset='feature_id',
                                              keep='first')
    labels = ""
    #labels = np.where(_merge_df.iloc[:,19]=='peak',1,0)
    data = _merge_df.iloc[:,17:].values
    
    return labels, data

def symlink_image(file='../../Img_Detect/tagged_table_for_image_detection.txt'):
    '''Takes an output metadata file from Zegami with images grouped by tags.
    Generates symbolic links in the tensorflow image detection tranining dataset
    that point to the raw images in ~ter119_CTCF_2/out/. Based on the value in
    the 'Tag' column this will put the link in the appropriate traning dataset
    sub-directory
    
    Parameters
    ----------
    file: tab-separated Zegami output with 'Tags' as the final column
    
    Output
    ------
    symbolic links in the appropriate tranining dataset sub-directory
    '''
    
    with open(file,'r') as w:
        for i in w.readlines()[1:]:
            cols = i.rstrip('\n').split('\t')
            ext = cols[1][:-4]+".jpg"
            dst = os.path.join('../../Img_Detect/training_dataset',
                               cols[-1],ext)
            src = os.path.join('/t1-data/user/staylor/zegami/ter119_CTCF_2/out',
                               ext)
            os.symlink(src, dst)
    return "symlinks created"

def filter_trained(tag_file='/t1-data1/WTSA_Dev/jkerry/MachineLearning/Zegami/zegamiml/dev/CTCF_with_doubles.tab',
                   full_file='/t1-data1/WTSA_Dev/jkerry/MachineLearning/Zegami/zegamiml/CTCF_plots_tables/PeakFeatures.tab'):
    df = pd.read_csv(full_file, sep='\t', header=0)
    df = df.drop_duplicates(subset='feature_id', keep='first')
    
    tag_df = pd.read_csv(tag_file, sep='\t', header=0)
    #train_list = os.listdir('/t1-data1/WTSA_Dev/jkerry/MachineLearning/Zegami/' \
    #                        'Img_Detect/training_dataset/null/')+os.listdir(
    #                        '/t1-data1/WTSA_Dev/jkerry/MachineLearning/Zegami/' \
    #                        'Img_Detect/training_dataset/peak/')
    #id_list = [x[:-4] for x in train_list]
    filter_df = df[[x not in tag_df['feature_id'].values for x in df['feature_id'].values]]
    return filter_df

#def classify(df):
#    for i in df['feature_id'][:5]:
#        image_name = i+".jpg"
#        script = '/t1-data1/WTSA_Dev/jkerry/MachineLearning/Zegami/Img_Detect/classify.py'
#        image_path = '/t1-data/user/staylor/zegami/ter119_CTCF_2/out/'+image_name
#        group = %run $script {image_path}
#    return group

