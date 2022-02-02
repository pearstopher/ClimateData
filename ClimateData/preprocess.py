import os
import sys
import csv
import numpy as np
import pandas as pd

datadir = './data/'
order = ['min', 'avg', 'max', 'precip']
filesToStrip = ['mintmp', 'avgtmp', 'maxtmp', 'precip']
colsPrefix = ['tmp-avg', 'tmp-max', 'tmp-min', 'precip']
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

if __name__ == '__main__':
    icols = [i for i in range(13)]
    dtypes = [str] + [str] * 12
    d = pd.DataFrame(np.vstack([icols, dtypes])).to_dict(orient='records')[1]

    dff = pd.DataFrame()

    for filename, prefix, i in zip(filesToStrip, colsPrefix, range(len(colsPrefix))):

        # Build column names
        cols = ['id']
        for m in months:
            cols.append(f'{prefix}-{m}')

        df = pd.read_csv(f'{datadir}climdiv-{filename}.csv', delimiter=',', header=None, index_col=False, usecols=icols, dtype=d)
        
        # Remove datatype field, since it's the same throughout the entirity of each file
        s = df.iloc[:,0]
        s = s.str[0:5] + s.str[7:]
        df.iloc[:,0] = s

        if i == 0:
            df.columns = cols
            dff = pd.DataFrame(df, columns=cols)
        else:
            df.columns = cols
            # Insure id parity here! 
            for v1, v2 in zip(dff.iloc[:,0], df.iloc[:,0]):
                if v1 != v2:
                    raise RuntimeError('Invalid Data Join')

            df = df.iloc[:,1:]
            dff = dff.join(df)

        print(dff)

        #df.to_csv(f'{datadir}{filename}.csv', header=False, index=False)
    dff.to_csv(f'{datadir}complete.csv', index=False)
    print('Succesful merge!')
