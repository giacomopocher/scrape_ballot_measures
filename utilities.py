
"""
Title: Scraping and Visualizing Raw Data about American Direct Democracy
Course: B2022 - Python for Economists
Instructor: Dr. Anatole Cheysson

Student: Giacomo Opocher
Position: 2nd Year PhD student in Economics
Institution: University of Bologna

Program Description: This code defines the funtions we need to scrape and 
analize data about the universe of ballot measures American citizens voted for
between 2018 and 2023. 
"""

"""
Description of the programming challenges

The goal of this code is to define a scraper that takes information from the 
public website Ballotpedia about the US ballot measures from 2018 to 2023.

We want to collect for each measure: title, date, state, link, result, contribution
amounts, readability score, closeness.

1.SCRAPING GENERAL INFORMATION
Ballotpedia has a page that collects type, title, date, state, description, link, and results 
(for some years) for each year. For instance, the link baseline_url = 
"https://ballotpedia.org/2022_ballot_measures" collects this information for 
the ballots in the year 2022.

The function scrape(link, election_year) takes the baseline url of a given election
year and scrapes the content of the tables you find under the header "By State".
This provides a list where each row is a table with dateXstate content. 

Each element of this list is itself a list containing type, title, description, 
results, link of all the measures in all the states for that election year. I 
scrape this information. 

A tricky passage is to retrieve the state. To do so, I use the link of the 
proposition that is attached on the column "Title" since I noticed that all
these links start with the State name.

I repeat this for each year, with some tricky challenges due to the different
formats that Ballotpedia adpopts year by year (e.g. not for all years we find the
number of votes for yes and no in the baseline_link, but in each measure's webpage).

2.SCRAPING READABILITY SCORES
Ballotpedia has a page that collects readability scores for all ballot measures,
given the election year. For instance, the link read_url = 
"https://ballotpedia.org/Ballot_measure_readability_scores,_2022" collects 
this information for the ballots in the year 2022.

The function scrape_read(link_year, election_year) scrapes the readabily scores
using a rational that is very similar to the scrape() function.
 
3.SCRAPING CONTRIBUTIONS DATA
Ballotpedia has a page that collects financial contributions in support or in
opposition for all ballot measures, given the election year. For instance, 
the link read_url = "https://ballotpedia.org/Ballot_measure_campaign_finance,_2022" 
collects this information for the ballots in the year 2022.

The function scrape_contributions(link_year, election_year) scrapes the amounts
spent in support or opposition of each ballot measure, using a rational that is 
very similar to the scrape() function.

4.AUXILIARY FUNCTIONS
I also have some auxiliary functions:
    1. state(url) and gen(date_url) extract the state and date information for 
       each proposition-specific link.
    2. hist, hist_by and plot_time generate standardized plots of the content 
       of interest.
    3. datecleaner cleans the date variable.

"""

### 0. Import the necessary packages
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, unquote
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt


### 1. Define the necessary functions
def state(url): 
    parsed_url = urlparse(url)
    path = unquote(parsed_url.path)
    parts = path.split('/')
    if len(parts) > 1:
        return parts[1].split('_')[0]  # Extract the first part before the first underscore
    return ""

def date_gen(url):
    start_pos = url.find('(') + 1
    end_pos = url.find(')')

    # Extract the date
    date_str = url[start_pos:end_pos].replace('_', ' ')
    return date_str

def scrape(link, election_year):
    # Prepare lists to store data
    titles = []
    types = []
    descriptions = []
    links = []
    states = []
    date = []
    votes_yes = []
    votes_no = []
    website = requests.get(link)
    page_content = BeautifulSoup(website.content, "html.parser")

    by_state_header = page_content.find(lambda tag: tag.name == "h2" and "By state" in tag.text)
    local_measures_header = page_content.find(lambda tag: tag.name == "h2" and "Local ballot measures" in tag.text)
    other_measures_header = page_content.find(lambda tag: tag.name == "h2" and "D.C. ballot measures" in tag.text)

    for elem in list(by_state_header.previous_siblings):
        elem.extract()

    if local_measures_header is not None:
        for elem in list(local_measures_header.next_siblings):
            elem.extract()    
            
    if other_measures_header is not None:
        for elem in list(other_measures_header.next_siblings):
            elem.extract()    

    all_blocks = page_content.find_all('table', attrs={'class': 'bptable'})

    for block in all_blocks:
        all_prop = block.find_all('tr')
        
        for proposition in all_prop[1:]:
            cells = proposition.find_all('td')
        
            type_text = cells[0].get_text(strip=True)
            title_text = cells[1].get_text(strip=True)
        
            if len(cells) == 4 or len(cells) == 5 or len(cells) == 7:
                description_text = cells[3].get_text(strip=True)
            else:
                description_text = cells[2].get_text(strip=True)
    
            link_text = cells[1].find('a').get('href')
            if link_text.startswith("https://ballotpedia.org"):
                link_text = link_text
            else:
                link_text = "https://ballotpedia.org" + f"{link_text}"
            state_text = state(link_text)
            date_text = date_gen(link_text)
            print(f'working on it...{title_text}, {state_text} ({date_text}) was crunchy to find')
         
            if len(cells) >= 6:
                votes_yes_t = cells[len(cells)-2].get_text(strip=True)
                votes_yes_t = float(votes_yes_t.split(' ')[0].replace(' ', '').replace(',', '').replace('.', ''))
                
                votes_no_t = cells[len(cells)-1].get_text(strip=True)
                votes_no_t = float(votes_no_t.split(' ')[0].replace(' ', '').replace(',', '').replace('.', ''))
            
            else: 
                if election_year != 2024:
                    votes_no_t = look_for_no(link_text)
                    votes_yes_t = look_for_yes(link_text)                        
                
            types.append(type_text)
            votes_no.append(votes_no_t)
            votes_yes.append(votes_yes_t)
            titles.append(title_text)
            descriptions.append(description_text)
            links.append(link_text)
            states.append(state_text)
            date.append(date_text)
        
        
    df = pd.DataFrame({
        'Type': types,
        'Title': titles,
        'Link': links,
        'State': states,
        'Description': descriptions,
        'Date': date,
        'Votes_Yes': votes_yes,
        'Votes_No': votes_no
    })

    del titles, links, states, types, descriptions, all_blocks, all_prop, cells, date 
    del type_text, title_text, link_text, state_text, description_text, link, website
    del votes_yes, votes_no, votes_yes_t, votes_no_t, date_text
    return df

def look_for_yes(link_prop):
    website_prop = requests.get(link_prop)
    results_page = BeautifulSoup(website_prop.content, "html.parser")
    results_header = results_page.find(lambda tag: tag.name == "h2" and "Election results" in tag.text)
    
    for elem in list(results_header.previous_siblings):
        elem.extract()
    
    block = results_page.find('table')
    all_res = block.find_all('tr')
    
    cells_yes = all_res[len(all_res)-2].find_all('td')
    votes_yes_t = cells_yes[1].get_text(strip=True)   
    votes_yes_t = float(votes_yes_t.replace(' ', '').replace(',', '').replace('.', ''))
        
    return votes_yes_t

def look_for_no(link_prop):
    website_prop = requests.get(link_prop)
    results_page = BeautifulSoup(website_prop.content, "html.parser")
    results_header = results_page.find(lambda tag: tag.name == "h2" and "Election results" in tag.text)
     
    for elem in list(results_header.previous_siblings):
        elem.extract()
    
    block = results_page.find('table')
    all_res = block.find_all('tr')
    
    cells_no = all_res[len(all_res)-1].find_all('td')
    votes_no_t = cells_no[1].get_text(strip=True)    
    votes_no_t = float(votes_no_t.replace(' ', '').replace(',', '').replace('.', ''))
    
    return votes_no_t

def scrape_read(link_read, election_year):
    title_grade = []
    title_ease= []
    link = []
    website_read = requests.get(link_read)
    results_page = BeautifulSoup(website_read.content, "html.parser")
    results_header = results_page.find(lambda tag: tag.name == "h2" and f"{election_year} readability scores" in tag.text)
    
    for elem in list(results_header.previous_siblings):
        elem.extract()
        
    block = results_page.find('table')
    
    all_prop = block.find_all('tr')
        
    for proposition in all_prop[1:]:
        cells = proposition.find_all('td')
        title_grade_text = (cells[1].get_text(strip=True))
        title_ease_text = (cells[2].get_text(strip=True))
        
        if title_grade_text == '':
            title_grade_text = 0
            title_ease_text = 0
            
        title_grade_text = float(title_grade_text)
        title_ease_text = float(title_ease_text)
            
        link_text = cells[0].find('a').get('href')
        if link_text.startswith("https://ballotpedia.org"):
            link_text = link_text
        else:
            link_text = "https://ballotpedia.org" + f"{link_text}"
            
        title_grade.append(title_grade_text)
        title_ease.append(title_ease_text)
        link.append(link_text)
    
    df = pd.DataFrame({
        'Title_Grade': title_grade,
        'Title_Ease': title_ease,
        'Link': link
    })
    
    return df

def scrape_contributions(link_contr, election_year):
    support_contr = []
    oppose_contr = []
    link = []
    
    website_contr = requests.get(link_contr)
    results_page = BeautifulSoup(website_contr.content, "html.parser")
    
    results_header = results_page.find(lambda tag: tag.name == "h2" and f"{election_year} ballot measure contributions" in tag.text)
    see_also_header = results_page.find(lambda tag: tag.name == "h2" and "See also" in tag.text)
    comparisons_header = results_page.find(lambda tag: tag.name == "h2" and "Comparison to prior years" in tag.text)
    per_year_header = results_page.find(lambda tag: tag.name == "h2" and "Contributions per vote analysis" in tag.text) 

    for elem in list(results_header.previous_siblings):
        elem.extract()

    if see_also_header is not None:
        for elem in list(see_also_header.next_siblings):
            elem.extract() 
        
    if comparisons_header is not None:
        for elem in list(comparisons_header.next_siblings):
            elem.extract() 
            
    if per_year_header is not None:
        for elem in list(per_year_header.next_siblings):
            elem.extract()             

    blocks = results_page.find_all('table')

    for table in blocks:
        all_prop = table.find_all('tr')

        for proposition in all_prop[1:]:
            cells = proposition.find_all('td')
            support_contr_t= cells[1].get_text(strip=True).replace('$', '').replace(',', '')
            oppose_contr_t = cells[2].get_text(strip=True).replace('$', '').replace(',', '')
            
            if support_contr_t== '':
                support_contr_t = 0
            
            if oppose_contr_t == '':
                oppose_contr_t = 0
                
            support_contr_t = float(support_contr_t)
            oppose_contr_t = float(oppose_contr_t)
            
            link_text = cells[0].find('a').get('href')
            if link_text.startswith("https://ballotpedia.org"):
                link_text = link_text
            else:
                link_text = "https://ballotpedia.org" + f"{link_text}"

            support_contr.append(support_contr_t)
            oppose_contr.append(oppose_contr_t)
            link.append(link_text)
        
    df = pd.DataFrame({
            'Support': support_contr,
            'Oppose': oppose_contr,
            'Link': link
        })

    return df

def hist(variable):
    plt.figure(figsize=(10, 6))  # Set the figure size
    plt.hist(variable, bins=50, color='skyblue', edgecolor='black')  # Customize bins and colors

    # Adding title and labels
    plt.title(f'Distribution of {variable.name}', fontsize=16)
    plt.xlabel(f'{variable.name}', fontsize=14)
    plt.ylabel('Frequency', fontsize=14)

    # Adding grid lines
    plt.grid(axis='y', alpha=0.75)

    # Customizing the ticks
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)

    # Adding a background style
    plt.style.use('seaborn-darkgrid')

def hist_by(variable, c_type):
    plt.figure(figsize=(10, 6))  # Set the figure size
    plt.hist(variable, bins=50, color='skyblue', edgecolor='black')  # Customize bins and colors

    # Adding title and labels
    plt.title(f'Distribution of {variable.name} for {c_type} Initiated Measures', fontsize=16)
    plt.xlabel(f'{variable.name}', fontsize=14)
    plt.ylabel('Frequency', fontsize=14)

    # Adding grid lines
    plt.grid(axis='y', alpha=0.75)

    # Customizing the ticks
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)

    # Adding a background style
    plt.style.use('seaborn-darkgrid')

def datecleaner(input_string):
    return float(''.join(re.findall(r'\d', input_string)))

def plot_time(x, y):    
    slope, intercept = np.polyfit(x, y, 1)
    
    plt.figure(figsize=(10, 6))  # Adjust the figure size as needed
    plt.scatter(x, y, marker='o', color='b', label='Closeness')
    plt.plot(x, slope*x + intercept, color='red', label='Linear fit')

    # Title and labels
    plt.title(f'{y.name} Over Time')
    plt.xlabel('Date')
    plt.ylabel(f'{y.name}')

    # Grid and legend
    plt.grid(True)
    plt.legend()

    # Show plot
    plt.show()

































