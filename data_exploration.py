import pandas as pd
import openpyxl
import matplotlib.pyplot as plt
import math
import os

FILENAMES = [
    '2018_11_07-general_election',
    '2019_04_02-spring_election',
    '2020_04_07-spring_election',
    '2020_08_11-partisan_primary',
    '2020_11_04-general_election',
    '2021_02_16-spring_primary',
    '2021_04_06-spring_election',
    '2022_02_15-spring_primary',
    '2022_04_05-spring_election',
    '2022_08_09-partisan_primary'
]
# df1 = pd.read_excel('data/2018_11_06_absentee_county.xlsx')

# df1.head()

# df2 = pd.read_excel('data/2018_11_07-general_election.xlsx')

# df2.head()

rdf = pd.read_csv('data/ruralurbancodes2013.csv')

rdf_wi = rdf[rdf['State']=='WI']
rdf_wi = rdf_wi[['County_Name', 'Population_2010', 'RUCC_2013', 'Description']]
rdf_wi['County_Name'] = rdf_wi['County_Name'].str.upper()
rdf_wi = rdf_wi.rename(columns={'County_Name': 'County'})

wi_fips = pd.read_csv('data/wi_county_fips.csv')
wi_fips['County Name'] = (wi_fips['County Name']).str.upper().apply(lambda x: x + ' COUNTY')
wi_fips = wi_fips.rename(columns={'County Name': 'County', 'FIPS Code': 'FIPS'})

def aggregate_absentee_data(filename):
    df = pd.read_excel('data/raw/' + filename + '.xlsx', engine='openpyxl')
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
    df_gb['turnout_%'] = df_gb['Total Voters']/df_gb['Population_2010']
    df_gb['absentee_%_of_voters'] = df_gb['absentees_counted']/df_gb['Total Voters']
    df_gb['absentee_%_of_population'] = df_gb['absentees_counted']/df_gb['Population_2010']
    df_gb['population_1000s'] = df_gb['Population_2010']/1000
    df_gb = pd.merge(df_gb, wi_fips[['County', 'FIPS']])

    # plt.scatter(
    #     x=df_gb['RUCC_2013'], 
    #     y=df_gb['absentee_%_of_voters'],
    #     s=df_gb['population_1000s']
    # )
    # plt.show()

    # plt.scatter(
    #     x=df_gb['population_1000s'], 
    #     y=df_gb['absentee_%_of_voters']
    # )
    # plt.show()

    df_gb.to_csv('data/cleaned/' + filename + '_agg.csv', index=False)

if __name__ == '__main__':
    for fl in FILENAMES:
        aggregate_absentee_data(fl)