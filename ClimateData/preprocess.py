import os
import sys
import csv
import numpy as np
import pandas as pd

datadir = './data/'
filesToStrip = ['avgtmp', 'maxtmp', 'mintmp', 'precip']

if __name__ == '__main__':
    cols = [i for i in range(13)]
    dtypes = [str] + [np.float] * 12
    d = pd.DataFrame(np.vstack([cols, dtypes])).to_dict(orient='records')

    for filename in filesToStrip:
        df = pd.read_csv(f'{datadir}climdiv-{filename}.csv', delimiter='  ', header=None, index_col=False)#, usecols=cols, dtype=d[1])
        
        s = df.iloc[:,0]
        s = s.str[0:5] + s.str[7:]
        df.iloc[:,0] = s

        df.to_csv(f'{datadir}{filename}.csv', header=False, index=False)
