
"""
Title: Scraping and Visualizing Raw Data about American Direct Democracy
Course: B2022 - Python for Economists
Instructor: Dr. Anatole Cheysson

Student: Giacomo Opocher
Position: 2nd Year PhD student in Economics
Institution: University of Bologna

Program Description: This code scrapes data about the ballot measure American
voters voted for between the years 2018 and 2023. See utilities.py for more
details on the functions from fn and for the structure of the websites.

N.B.: it takes some time (appr. 20 mins) to run because it goes in each propositions' 
      website to retrieve some info.
"""

"""
Description of the Insighs

The focus of this project is on the scraping part. However, some interesting
insights can be drawn from this (very) preliminary graphical analysis:
    1. The interest of American Voters for ballot measures (measured as closeness, 
       total number of votes, and support to citizens initiated propositions)
       is stable over time.
    2. Overall, it is more volatile for citizens initiated ballots and slightly
       higher.
    3. The readability of measures' titles is low, with small differences over type
       and remained low over time.
"""
####### 0. Import the necessary packages. #####################################
import pandas as pd
import utilities as fn



###### 1. Scrape the information of interest from Ballotpedia. ################

# Generate empty DF where to store information
df = pd.DataFrame(columns=['Type','Title','Link','State','Description','Date',
                           'Votes_Yes', 'Votes_No'])

df_read = pd.DataFrame(columns=['Title_Grade','Title_Ease','Link'])

df_contr = pd.DataFrame(columns=['Support','Oppose','Link']) 

# Scrape the data for the years of interest
for year in range(2018, 2024, 1): 
    link = f"https://ballotpedia.org/{year}_ballot_measures"
    link_read = f"https://ballotpedia.org/Ballot_measure_readability_scores,_{year}"
    link_contr = f"https://ballotpedia.org/Ballot_measure_campaign_finance,_{year}"
    
    #scrape contributions
    data_contr = fn.scrape_contributions(link_contr, year)
    df_contr = pd.concat([df_contr, data_contr], ignore_index=True)
    print(f"... retrieving contributions amounts for the year {year}")
    
    #scrape readability index
    data_read = fn.scrape_read(link_read, year)
    df_read = pd.concat([df_read, data_read], ignore_index=True)
    print(f"... retrieving readability scores for the year {year}")
    
    #scrape general info
    data = fn.scrape(link, year)
    df = pd.concat([df, data], ignore_index=True)
    print(f'We got you Joe, ballot measures from {year} have been stored!! :)')
    del link, year, data_read, link_read, data 

# Merge DFs with general information, readability scores, contributions
final_data = pd.merge(df_read, df_contr, on='Link', how='outer')
final_data = pd.merge(df, final_data, on='Link', how='outer')

# Delete useless stuff
del df, df_contr, df_read, data_contr, link_contr

# Clean and define the variables of interest for the analysis
final_data['Closeness'] = final_data['Votes_Yes'] - final_data['Votes_No']

# Drop NAs
final_data = final_data.dropna(subset=['Type'])

# Drop a weird one
final_data = final_data[final_data['Date'] != "TIF"]

# Clean the date variable
final_data['Date'] = final_data['Date'].apply(fn.datecleaner)

# Define a variable that subsets all the Citizens intiated ballot measures
final_data['cit_init'] = final_data['Type'].str.startswith('C').astype(int)

# Count total votes
final_data['Total Votes'] = final_data['Votes_Yes'] + final_data['Votes_No']


###### 2. Visualize the Raw Data ##############################################

# Overall closeness
fn.hist(final_data['Closeness'])
fn.plot_time(final_data['Date'], final_data['Closeness'])
# Closeness remained more or less stable over time


# Closeness for type of initiative: citizens or legislation initiated
fn.hist_by(final_data['Closeness'][final_data['cit_init']==1], 'Citizens')
fn.hist_by(final_data['Closeness'][final_data['cit_init']==0], 'Legislature')


# Total number of votes over time
fn.hist(final_data['Total Votes'])
fn.plot_time(final_data['Date'], final_data['Total Votes'])

# Total number of votes by type
fn.hist_by(final_data['Total Votes'][final_data['cit_init']==1], 'Citizens')
fn.hist_by(final_data['Total Votes'][final_data['cit_init']==0], 'Legislature')

# Contributions amounts
fn.hist(final_data['Support'])
fn.plot_time(final_data['Date'], final_data['Support'])
fn.hist(final_data['Oppose'])
fn.plot_time(final_data['Date'], final_data['Oppose'])

# Contributions amounts by type
fn.hist_by(final_data['Support'][final_data['cit_init']==1], 'Citizens')
fn.hist_by(final_data['Support'][final_data['cit_init']==0], 'Legislature')

# Readability scores over time and by type
fn.hist_by(final_data['Title_Grade'][final_data['cit_init']==1], 'Citizens')
fn.hist_by(final_data['Title_Grade'][final_data['cit_init']==0], 'Legislature')

fn.plot_time(final_data['Date'][final_data['cit_init']==1], 
             final_data['Title_Grade'][final_data['cit_init']==1])

fn.plot_time(final_data['Date'][final_data['cit_init']==0], 
             final_data['Title_Grade'][final_data['cit_init']==0])

