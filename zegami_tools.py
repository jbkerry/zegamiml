#!/usr/bin/env python

import pandas as pd

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
    
    _temp_df = pd.read_csv(table, sep='\t', header=0)
    _temp_df['plot_name'] = name
    _temp_df['peak_type'] = peak_type
    _temp_df['position'] = position
    update_df = df.append(_temp_df, ignore_index=True)
    
    return update_df

def merge_plot_data(df, plot_file, dd=True):
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
    
    #_zegami_mat = pd.read_csv('PeakFeatures.tab',sep="\t")
    _zegami_df = df
    
    _merge_df = pd.merge(_zegami_df, _data_df, on='feature_id')
    if dd:
        _merge_df = _merge_df.drop_duplicates(subset='feature_id',
                                              keep='first')
    
    data = _merge_df.iloc[:,23:].values
    
    return data
