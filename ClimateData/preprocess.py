import os
import sys
import csv
import numpy as np
import pandas as pd

datadir = './data/raw/'
outputDir = './data/processed/'
order = ['min', 'avg', 'max', 'precip']
filesToStrip = ['mintmp', 'avgtmp', 'maxtmp', 'precip']
colsPrefix = ['tmp-avg', 'tmp-max', 'tmp-min', 'precip']
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

if __name__ == '__main__':
    dff = pd.DataFrame()
    icols = [i for i in range(13)]

    for filename, prefix, i in zip(filesToStrip, colsPrefix, range(len(colsPrefix))):

        # Build column names
        cols = ['id INTEGER PRIMARY KEY']
        for m in months:
            cols.append(f'{prefix}-{m} FLOAT')

        df = pd.read_csv(f'{datadir}climdiv-{filename}.csv', delimiter=',', header=None, index_col=False, usecols=icols, dtype=d)
        
        # Remove datatype field, since it's the same throughout the entirity of each file
        s = df.iloc[:,0]
        s = s.str[0:5] + s.str[7:]
        df.iloc[:,0] = s

        if i == 0:
            # Add USA Country code
            cc = pd.DataFrame(['01']*len(df), dtype=(str))
            df.iloc[:,0] = cc.iloc[:,0].str[:] + df.iloc[:,0].str[:]

            # Add columns (along with id column this first time)
            df.columns = cols
            dff = pd.DataFrame(df, columns=cols)
        else:
            # Add columns
            df.columns = cols
            # Insure id parity here! 
            for v1, v2 in zip(dff.iloc[:,0], df.iloc[:,0]):
                # Don't compare country code as it hasn't been added to anything but the primary id
                if v1[2:] != v2:
                    raise RuntimeError('Invalid Data Join')

            df = df.iloc[:,1:]
            dff = dff.join(df)

        print(dff)

        # Create individual files
        #df.to_csv(f'{datadir}{filename}.csv', header=False, index=False)

    # WARNING: If you open this file in Excel without specifying the first 
    # column is a string, it will remove all the first zeros in the ID column
    dff.to_csv(f'{outputDir}complete.csv', index=False)
    print('Succesful merge!')
