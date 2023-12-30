import os
import json

def get_and_categorize_news_all(file_names):
    directory = "current_news"
    if not os.path.exists(directory):
        os.makedirs(directory)

    all_news = {}

    # Load regional news from the specified file names
    for file_name in file_names:
        full_file_path = os.path.join("news_json", file_name)
        with open(full_file_path, "r") as f:
            news_data = json.load(f)
        
        # Extract the country code from the file name (assuming it's in the format "{country}-regional-news.json")
        country_code = file_name.split('-')[1] if '-' in file_name else 'INT'
        
        # Append the news articles to the corresponding country in all_news
        all_news[country_code] = all_news.get(country_code, []) + news_data.get('articles', [])

    # Prepare the data to be saved as JSON
    data_to_save = {
        "status": "ok",
        "totalResults": sum(len(articles) for articles in all_news.values()),
        "articles": [article for articles in all_news.values() for article in articles],
    }
    
    # Save the aggregated news to a new file
    filename = os.path.join(directory, "current-news.json")
    with open(filename, "w") as f:
        json.dump(data_to_save, f, indent=4)  # Use indent=4 for pretty formatting

    print(f"Data saved as {filename}")

    return all_news

# Example usage:
file_names = [
    "2023-06-22_00-13-us-regional-news.json",
    "2023-06-22_00-46-us-regional-news.json",
    "2023-06-22_00-49-ru-regional-news.json",
    "2023-06-22_00-50-il-regional-news.json",
    "2023-06-22_00-51-sa-regional-news.json",
    "2023-06-22_00-53-ae-regional-news.json",
    "2023-06-22_00-55-tr-regional-news.json",
    "2023-06-22_00-56-technology-news.json",
    "2023-06-22_00-58-science-news.json"
]

all_news = get_and_categorize_news_all(file_names)
