import requests
from bs4 import BeautifulSoup
import csv
from deep_translator import GoogleTranslator

# Define the target URL
base_url = "https://www.oxfordlearnersdictionaries.com"
wordlist_url = f"{base_url}/wordlists/oxford3000-5000"

# Send a GET request to the website
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
}
response = requests.get(wordlist_url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Define the levels to scrape
    levels = ['a1', 'a2', 'b1', 'b2', 'c1', 'c2']
    
    # Prepare CSV file for writing line by line
    csv_file = "oxford_words.csv"
    with open(csv_file, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.DictWriter(file, fieldnames=['number', 'word', 'translation', 'part_of_speech', 'oxford_list_level', 'detected_level'])
        writer.writeheader()
        
        # Loop through each level
        word_counter = 1
        for level in levels:
            print(f"Scraping words for level: {level.upper()}")
            word_elements = soup.find_all('li', {'data-ox5000': level})
            
            for element in word_elements:
                word = element.get('data-hw')
                pos_element = element.find(class_='pos')
                part_of_speech = pos_element.text.strip() if pos_element else 'Unknown'
                
                # Fetch the word definition page to find the level
                word_url = f"{base_url}/definition/english/{word}"
                word_response = requests.get(word_url, headers=headers)
                word_level = 'Unknown'
                
                if word_response.status_code == 200:
                    word_soup = BeautifulSoup(word_response.content, 'html.parser')
                    level_element = word_soup.find(class_=lambda x: x and ('ox3ksym' in x or 'ox5ksym' in x))
                    if level_element:
                        word_level = level_element.get('class')[0].split('_')[-1].upper()  # Extract level like B2, C1
                
                # Translate word from English to Thai using deep-translator
                try:
                    translation = GoogleTranslator(source='en', target='th').translate(word)
                except Exception as e:
                    translation = 'Translation Error'
                    print(f"Translation failed for {word}: {e}")
                
                # Write the data directly to CSV line by line to save memory
                writer.writerow({
                    'number': word_counter,
                    'word': word,
                    'translation': translation,
                    'part_of_speech': part_of_speech,
                    'oxford_list_level': level.upper(),
                    'detected_level': word_level
                })
                
                # Print word data with loop number and translation
                print(f"{word_counter}. Word: {word}, Translation: {translation}, Part of Speech: {part_of_speech}, Oxford List Level: {level.upper()}, Detected Level: {word_level}")
                
                word_counter += 1

    print(f"Data successfully saved to {csv_file}")

else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")