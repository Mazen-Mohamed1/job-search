import requests
from bs4 import BeautifulSoup
import csv
import os
import PySimpleGUI as sg
import re

# checking if the internet is working
def is_internet_available():
    try:
        # Try to make a request to a well-known server (e.g., Google's DNS)
        response = requests.get('http://www.google.com', timeout=5)
        # If the request was successful (status code 200), return True
        return response.status_code == 200
    except requests.ConnectionError:
        # If there was a connection error, return False
        return False

# simple GUI
sg.theme('DarkTeal9')

layout = [
    [sg.Text('JOB TITLE: ', size=(15, 1)), sg.InputText(key='Name', enable_events=True)],
    [sg.Submit(), sg.Button('Clear'), sg.Exit()],
    [sg.Text('', size=(20, 1), key='loading_text', visible=False)]

]


window = sg.Window('Please Enter the JOB TITLE', layout)

def Clear_input():
    for key in values:
        window[key]('')
    return None


job_search = ""
counting = 0
page_limit = 0
job_details = []  # Initialize the job_details list

def get_page_data(page_num, job):

    url = f'https://wuzzuf.net/search/jobs/?a=hpb&filters%5Bcountry%5D%5B0%5D=Egypt&q={job}&start={page_num}'
    page = requests.get(url)
    return page

def printing_file():
    # Write all the data to the CSV file after processing all pages
    path = rf"{os.path.dirname(os.path.abspath(__file__))}\jobs-details.csv"
    keys = job_details[0].keys()

    with open(path, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(job_details)

def main(page):
    global job_details  # Reference the global variable
    global counting

    src = page.content
    soup = BeautifulSoup(src, 'lxml')

    job_titles = soup.find_all('h2', {'class': 'css-m604qf'})
    companies_names = soup.find_all('div', {'class': 'css-d7j1kk'})
    companies_locations = soup.find_all('div', {'class': 'css-d7j1kk'})
    old_post = soup.find_all('div', {'class': 'css-4c4ojb'})
    new_post = soup.find_all('div', {'class': 'css-do6t5g'})
    posts_date = [*new_post, *old_post]

    global page_limit
    page_limit = int(soup.find('strong').text.strip())

    for i in range(len(job_titles)):
        job_title = job_titles[i].find('a').text.strip()
        links = job_titles[i].find('a')['href']
        company_name = companies_names[i].find('a').text.strip()
        company_location = companies_locations[i].find('span').text.strip()
        post_date = posts_date[i].text.strip()
        requirements = soup.find_all('div', {'class': 'css-y4udm8'})
        requirement = requirements[i].find_all('span')
        job_res = [span.get_text(strip=True) for span in requirement]
        job_res_str = ', '.join(job_res)

        job_details.append({
            'JOB TITLE': job_title,
            'COMPANY NAME': company_name,
            'POST DATE': post_date,
            'COMPANY LOCATION': company_location,
            'JOB TIME': job_res_str,
            'JOB LINK': links
        })

    counting += 1
    if counting > page_limit // 15:
        return True  # Indicate that there are no more pages to process
    else:
        return False  # Continue processing pages


if not is_internet_available():
    sg.popup("Please, open the Wifi")
else:
    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == "Exit":
            break

        elif event == "Clear":
            # Check for empty fields
            if values and any(value == "" for value in values.values()):
                sg.popup("Please, fill out the fields")
            else:
                Clear_input()

        elif event == "Submit":
            # Check for empty fields
            if values and any(value == "" for value in values.values()):
                sg.popup("Please, fill out the fields")

            elif values.get('Name', ''):
                job_search = values['Name']

                # Check if there is exactly one space between each word
                if not re.match(r'^[^\s\d]+ [^\s\d]+$', job_search):
                    sg.popup("Please use one space between each word")
                    continue
                else:
                    while True:
                        # Show loading text
                        window['loading_text'].update('Loading...', visible=True)
                        window.refresh()
                        page = get_page_data(counting, job_search.replace(' ', '+'))
                        should_break = main(page)
                        if should_break:
                            sg.popup(f"{page_limit} job has been found")
                            printing_file()
                            sg.popup(f"File Created Successfully")
                            # Hide loading text
                            window['loading_text'].update(visible=False)
                            window.close()
                            break







