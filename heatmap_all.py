# To create a heatmap at the state level, based on percentage of "true" online learning keywords
import pandas as pd
import numpy as np

# Load dataset
mergedDfAll = pd.read_csv("mergedDfAll.csv")
mergedDfAll.head()

# Select the onlineFlg and county columns
mergedDfOnlFlg = mergedDfAll[['onlineFlg', 'County']]
mergedDfOnlFlg.head(3)

# Group onlineFlg by county
mergedDfOnlFlg['onlineFlg']=mergedDfOnlFlg['onlineFlg'].astype(str)
descriptiveOnl = mergedDfOnlFlg.groupby('County').describe()
descriptiveOnl.head()

# Calculate percentage "true" online flg = frequency of true/count of schools by county
# If true, percent true = freq true/count
# If false, percent true = 1-(freq false/count)

descriptiveOnl2['top'] = descriptiveOnl2['top'].astype(str)
descriptiveOnl2['percentTrue'] = np.where(descriptiveOnl2['top']=="True", descriptiveOnl2['freq']/descriptiveOnl2['count'],
                                         1-(descriptiveOnl2['freq']/descriptiveOnl2['count']))

# View decriptive stats for percentage true
descriptiveOnl2.percentTrue.describe()

# Group based on percentile of percentTrue
def groupDf(df):
    if (df["percentTrue"]<=.25):
        return "G1"
    elif (df["percentTrue"]>.25) and (df["percentTrue"]<=.50):
        return "G2"
    elif (df["percentTrue"]>=.50) and (df["percentTrue"]<=.75):
        return "G3"
    else:
        return "G4"
descriptiveOnl2['group']=descriptiveOnl2.apply(groupDf, axis=1)

# Sort group by group categories
groupSort = descriptiveOnl2.groupby('group').agg({'county':lambda x: list(x)})

# Write group to list to prepare .csv stylesheet for the heatmap
g2 = groupSort.values[0].tolist()
g3 = groupSort.values[1].tolist()
g4 = groupSort.values[2].tolist()

# Check results for group list
g4

# Now that we have a list of counties, prepare css styles for the heatmap. Replace the fill code with any hex codes you'd like.
for i in g2[0]:
    print("."+str(i)+" "+"{fill:#c3c1f2;}")
for i in g3[0]:
    print("."+str(i)+" "+"{fill:#c17a70;}")
for i in g4[0]:
    print("."+str(i)+" "+"{fill:#1a1835;}")
