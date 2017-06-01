#!/usr/bin/env python

import pandas as pd

def reset():
    '''Starts as new data-frame or can be used to reset
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
    update_df: updated df consisting of original plus the new data-frame
    
    '''
    
    _temp_df = pd.read_csv(table, sep='\t', header=0)
    _temp_df['plot_name'] = name
    _temp_df['peak_type'] = peak_type
    _temp_df['position'] = position
    update_df = df.append(_temp_df, ignore_index=True)
    
    return update_df
