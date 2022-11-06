import pandas as pd
import openpyxl
import matplotlib.pyplot as plt
import math

FILENAMES = [
    '2018_11_07_all_ward',
    '2020_04_07_all_ward'
]
df1 = pd.read_excel('data/2018_11_06_absentee_county.xlsx')

df1.head()

df2 = pd.read_excel('data/2018_11_07_all_ward.xlsx')

df2.head()

rdf = pd.read_csv('data/ruralurbancodes2013.csv')

rdf_wi = rdf[rdf['State']=='WI']
rdf_wi = rdf_wi[['County_Name', 'Population_2010', 'RUCC_2013', 'Description']]
rdf_wi['County_Name'] = rdf_wi['County_Name'].str.upper()
rdf_wi = rdf_wi.rename(columns={'County_Name': 'County'})

def aggregate_absentee_data(filename):
    df = pd.read_excel('data/' + filename + '.xlsx', engine='openpyxl')
    if 'Mililary Absentees Transmitted Issued' in df.columns:
        df = df.rename({'Mililary Absentees Transmitted Issued': 'Military Absentees Transmitted Issued'})
    if 'Mililary Absentees Transmitted Counted' in df.columns:
        df = df.rename({'Mililary Absentees Transmitted Counted': 'Military Absentees Transmitted Counted'})
    df['Election'] = filename
    df['absentees_issued'] = (
        df['In Person Absentees Issued'] + 
        df['Non UOCAVA Absentees Transmitted Issued'] +
        df['Mililary Absentees Transmitted Issued'] +
        df['Temporarily Overseas Absentees Transmitted Issued'] +
        df['Permanent Overseas Absentees Transmitted Issued']
    )

    df['absentees_counted'] = (
        df['In Person Absentees Counted']  +
        df['Non UOCAVA Absentees Transmitted Counted'] +
        df['Mililary Absentees Transmitted Counted'] +
        df['Temporarily Overseas Absentees Transmitted Counted'] +
        df['Permanent Overseas Absentees Transmitted Counted']
    )

    df_gb = df.groupby(['County', 'Election']).agg({
        'absentees_issued':'sum', 
        'absentees_counted': 'sum',
        'Total Voters': 'sum',
        'Total Ballots': 'sum'
    }).reset_index()

    df_gb = pd.merge(df_gb, rdf_wi)
    df_gb['Population_2010'] = [x.replace(',','') for x in df_gb['Population_2010']]
    df_gb['Population_2010'] = df_gb['Population_2010'].astype(float)
    df_gb['turnout'] = df_gb['Total Ballots']/df_gb['Population_2010']
    df_gb['absentee_%_of_ballots'] = df_gb['absentees_counted']/df_gb['Total Voters']
    df_gb['absentee_%_of_population'] = df_gb['absentees_counted']/df_gb['Population_2010']
    df_gb['population_1000s'] = df_gb['Population_2010']/1000

    plt.scatter(
        x=df_gb['RUCC_2013'], 
        y=df_gb['absentee_%_of_ballots'],
        s=df_gb['population_1000s']
    )
    plt.show()

    plt.scatter(
        x=df_gb['population_1000s'], 
        y=df_gb['absentee_%_of_ballots']
    )
    plt.show()

    df_gb.to_csv('data/' + filename + '_agg.csv', index=False)

if __name__ == '__main__':
    for fl in FILENAMES:
        aggregate_absentee_data(fl)