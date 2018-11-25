import matplotlib.pyplot as plt
import pandas as pd
import numpy as np



# index | col A | col B |
# A     | 1    | N/A   |
# B     | N/A   | 2     |

def merge_op(df1, df2):
    if df1.columns.contains(df2.columns[0]):
        return pd.merge(df1, df2, on=df2.columns[0])
    else:
        return pd.concat([df1, df2], axis=1, sort=False)
    #return df.append(df2)

s = pd.Series([1], index=['A'], name='ColA')
df = pd.DataFrame(s, dtype=int)
print(df)

s = pd.Series([2], index=['B'], name='ColB')
df2 = pd.DataFrame(s, dtype=int)
df = merge_op(df, df2)
print(df)

s = pd.Series([3], index=['A'], name='ColC')
df2 = pd.DataFrame(s, dtype=int)
df = merge_op(df, df2)
print(df)

s = pd.Series([3], index=['B'], name='ColA')
df2 = pd.DataFrame(s, dtype=int)
df = merge_op(df, df2)
print(df)
