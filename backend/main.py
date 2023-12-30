from flask import Flask, send_file
from flask_cors import CORS
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
from tenacity import retry, wait_exponential, stop_after_attempt
from urllib.parse import urljoin
from google.cloud import translate_v2 as translate
import os.path
import threading
import json
import requests
import openai
import schedule
import time

def scheduled_news_collection():
    try:
        get_and_categorize_news_all(news_api_key, regions, categories)
    except Exception as e:
        print(f"Error while running scheduled news collection: {str(e)}")

schedule.every(6).hours.do(scheduled_news_collection)

app = Flask(__name__)
CORS(app)

load_dotenv()

openai_api_key = os.getenv('OPENAI')
news_api_key = os.getenv('NEWS')
regions = ["us", "ru", "il", "sa", "ae", "tr"]
categories = ["technology", "science"]
# Set the Google Application Credentials environment variable
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./credentials.json"


@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=10))
def make_openai_request(model, messages, temperature, max_tokens):
    openai.api_key = openai_api_key
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response
    except Exception as e:
        raise Exception(f"OpenAI API error encountered: {e}")

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=10))
def make_news_api_request(URL):
    try:
        response = requests.get(url=URL)
        data = response.json()
        return data
    except Exception as e:
        raise Exception(f"News API error encountered: {e}")

def scrape_article(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        paragraphs = soup.find_all('p')
        article_content = ' '.join([p.text for p in paragraphs])

        # Use the summarize_text function to get the summarized content
        summarized_content = summarize_text(article_content)

        return summarized_content
    except requests.exceptions.RequestException as e:
        print(f"Failed to scrape {url}. Error: {e}")
        return None

def fetch_image_if_none(article):
    if not article['urlToImage']:
        try:
            response = requests.get(article['url'])
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Fetch the first image in the webpage
            image_tag = soup.find('img')
            
            if image_tag and 'src' in image_tag.attrs:
                # Ensure the URL is absolute
                image_url = urljoin(article['url'], image_tag['src'])
                article['urlToImage'] = image_url
        except requests.exceptions.RequestException as e:
            print(f"Failed to scrape {article['url']} for image. Error: {e}")
    
    return article

# Create a translation client
translate_client = translate.Client()

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=30))
def translate_with_retry(title, target='en'):
    result = translate_client.translate(title, target_language=target)
    return result['translatedText']

def translate_headline(title):
    # Detect the language of the title
    result = translate_client.detect_language(title)
    detected_lang = result['language']

    # If the detected language is not Turkish, Arabic or English, translate the title to English
    if detected_lang not in ['tr', 'ar', 'en']:
        try:
            translated_title = translate_with_retry(title)
            return translated_title
        except Exception as e:
            print(f"Failed to translate title. Error: {e}")
            # If translation fails after retries, return the original title

    return title

def categorize_text(title, description):
    messages=[
        {"role": "system", "content": 'You are a helpful assistant that categorizes news articles into one of three categories: "Political", "Business and Economy", or "General". Based on the title and description of the article, determine the category it falls under. Respond with ONLY the category and nothing else'},
        {"role": "user", "content": f"""
        Here is a news article:

        Title: {title}
        Description: {description}

        Please categorize this news article. For example, if the article is about a new government policy, it would fall under the "Political" category. If it discusses stock market trends, it would be "Business and Economy". If it's about a general interest topic, like a local event or a celebrity, it would be categorized as "General".
        """}
    ]
    try:
        response = make_openai_request("gpt-3.5-turbo", messages, 0, 60)
        category = response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Failed to categorize text. Error: {e}")
        category = "Uncategorized"
    return category


def summarize_text(input_text):
    # Split the text into words
    words = input_text.split()
    # Take exactly the first 500 words
    first_500_words = ' '.join(words[:500])
    # Check if the text has been cut to exactly 500 words
    # If it is, add ellipsis (...) to indicate that the text continues
    if len(words) > 500:
        first_500_words += '...'
    # Start a chat with GPT-3.5-turbo
    messages=[
        {"role": "system", "content": 'You are a helpful assistant that can summarize long text which is scraped from news articles into a short description which is suitable for use in a mobile news app. If the provided text by the user is an ad banner, cookie settings, permissions, pop-ups, or any other text that is generally irrelevant and serves no purpose or if you have not been provided any text then return "This newspaper has no description, please click on the link to learn more" ONLY.'},
        {"role": "user", "content": f"""
        Please provide a summary in English for the following text scraped from a news article:

        {first_500_words}
        """}
    ]
    try:    
        # Extract the summary from GPT-3.5-turbo's response
        response = make_openai_request("gpt-3.5-turbo", messages, 0.2, 500)
        summary = response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Failed to summarize text. Error: {e}")
        summary = "Text could not be summarized"

    return summary



def get_regional_news(news_api_key, regions):
    directory = "news_json"
    if not os.path.exists(directory):
        os.makedirs(directory)

    for country in regions:
        URL = f"https://newsapi.org/v2/top-headlines?country={country}&apiKey={news_api_key}"
        
        data = make_news_api_request(URL)

        for article in data.get('articles', []):
            # Fetch image if none
            article = fetch_image_if_none(article)

            # Translate headline if necessary
            article['title'] = translate_headline(article['title'])

            article['country'] = country

            if not article['description']:
                article['description'] = scrape_article(article['url'])
            
            # Get the category for each article using the title and description
            article['category'] = categorize_text(article['title'], article['description'])

        current_date = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = os.path.join(directory, f"{current_date}-{country}-regional-news.json")

        with open(filename, "w") as f:
            json.dump(data, f)
        
        print(f"Data saved as {filename}")

    return data


def get_science_and_tech_news(news_api_key, categories):
    directory = "news_json"
    if not os.path.exists(directory):
        os.makedirs(directory)

    for category in categories:
        URL = f"https://newsapi.org/v2/top-headlines?category={category}&apiKey={news_api_key}"
        
        data = make_news_api_request(URL)

        for article in data.get('articles', []):
            # Fetch image if none
            article = fetch_image_if_none(article)

            # Translate headline if necessary
            article['title'] = translate_headline(article['title'])

            if not article['description']:
                article['description'] = scrape_article(article['url'])

            # Assign 'country' as 'INT'
            article['country'] = 'INT'

        current_date = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = os.path.join(directory, f"{current_date}-{category}-news.json")

        with open(filename, "w") as f:
            json.dump(data, f)
        
        print(f"Data saved as {filename}")

    return data


def get_and_categorize_news_all(news_api_key, regions, categories):
    directory = "current_news"
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    all_news = {}

    regional_news = get_regional_news(news_api_key, regions)
    science_tech_news = get_science_and_tech_news(news_api_key, categories)

    for country in regions:
        all_news[country] = regional_news.get('articles', [])

    for category in categories:
        for country in all_news.keys():
            all_news[country] += [article for article in science_tech_news.get('articles', []) if article['country'] == country]

    # Save the aggregated news to a new file
    filename = os.path.join(directory, "current-news.json")
    data_to_save = {
        "status": "ok",
        "totalResults": sum(len(articles) for articles in all_news.values()),
        "articles": [article for articles in all_news.values() for article in articles],
    }

    with open(filename, "w") as f:
        json.dump(data_to_save, f)

    print(f"Data saved as {filename}")

    return all_news


@app.route('/api/news', methods=['GET'])
def get_all_news_api():
    directory = "current_news"
    filename = os.path.join(directory, "current-news.json")

    try:
        return send_file(filename, mimetype='application/json')
    except FileNotFoundError:
        return {"error": "File not found"}, 404

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Call the function to start the news collection immediately
scheduled_news_collection()

# Run the schedule in a separate thread
scheduler_thread = threading.Thread(target=run_schedule)
scheduler_thread.start()

if __name__ == "__main__":
    app.run()