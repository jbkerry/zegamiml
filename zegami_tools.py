#!/usr/bin/env python

import os
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
    
    temp_df = pd.read_csv(table, sep='\t', header=0)
    temp_df['plot_name'] = name
    temp_df['peak_type'] = peak_type
    temp_df['position'] = position
    update_df = df.append(temp_df, ignore_index=True)
    
    return update_df

def get_plot_data(zegami_file, plot_file, col_num):
    '''Merges peaks in a zegami output dataframe with
    plot data from a text file with bigWig values in
    100 bins across the peak
    
    Parameters
    ----------
    zegami_file: the zegami info TSV file with the required peak IDs
    plot_file: a tab-delimited file with values for
        all peaks, split into 100 bins (output from deepTools computeMatrix)
    col_num: int, the number of columns in the zegami data-frame
        
    Returns
    -------
    zegami_df: a pandas data-frame of the original zegami input file
    merge_df: a pandas data-frame (n x 101) containing the 100 bins with bigwig
        plot data from plot_file and the corresponding peak feature_id
    '''
    
    data_df = pd.read_csv(plot_file,sep='\t',skiprows=1,header=None)
    data_df = data_df.fillna(0)
    data_df.insert(0, 'feature_id', data_df[0]+"_"+data_df[1].map(str)+"_"+data_df[2].map(str))
    data_df = data_df.drop_duplicates(subset='feature_id', keep='first')
    
    zegami_df = pd.read_csv(zegami_file, sep="\t", header=0)
    zegami_df = zegami_df.drop_duplicates(subset='feature_id', keep='first')
    zegami_df.index = range(zegami_df.shape[0])
    
    merge_df = pd.merge(zegami_df, data_df, on='feature_id')                                  
    plot_start = col_num+6
    merge_df = merge_df.iloc[:, [0] + [i for i in range(plot_start,
                                                        plot_start+100)]]
    
    if not zegami_df['feature_id'].equals(merge_df['feature_id']):
        print('Caution: original zegami data-frame and merged data-frame are' \
              ' not in the same order')
    
    return zegami_df, merge_df

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

def filter_trained(file='/t1-data1/WTSA_Dev/jkerry/MachineLearning/Zegami/zegamiml/PeakFeatures.tab'):
    df = pd.read_csv(file, sep='\t', header=0)
    df = df.drop_duplicates(subset='feature_id', keep='first')
    train_list = os.listdir('/t1-data1/WTSA_Dev/jkerry/MachineLearning/Zegami/' \
                            'Img_Detect/training_dataset/null/')+os.listdir(
                            '/t1-data1/WTSA_Dev/jkerry/MachineLearning/Zegami/' \
                            'Img_Detect/training_dataset/peak/')
    id_list = [x[:-4] for x in train_list]
    filter_df = df[[x not in id_list for x in df['feature_id']]]
    return filter_df

def classify(df):
    for i in df['feature_id'][:5]:
        image_name = i+".jpg"
        script = '/t1-data1/WTSA_Dev/jkerry/MachineLearning/Zegami/Img_Detect/classify.py'
        image_path = '/t1-data/user/staylor/zegami/ter119_CTCF_2/out/'+image_name
        #group = %run $script {image_path}
    #return group
    
    ### since no browser is installed on harrier I ran the following from an ipython shell instead of this function:
   # for i in filter_df['feature_id']:
   #...:     image_name = i+'.jpg'
   #...:     script = '/t1-data1/WTSA_Dev/jkerry/MachineLearning/Zegami/Img_Detect/classify.py'
   #...:     image_path = '/t1-data/user/staylor/zegami/ter119_CTCF_2/out/'+image_name
   #...:     with io.capture_output() as captured:
   #...:         %run $script {image_path}
   #...:     for line in captured.stdout.split('\n'):
   #...:         if line:
   #...:             label, score = line.split(' (score = ')
   #...:             score = score.rstrip(')')
   #...:             score_dict[label].append(score)
