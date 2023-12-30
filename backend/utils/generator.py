from datetime import datetime
import os.path
import json


def generate_message2(regions, regional_directory, techsci_categories, techsci_directory):
    message = "<h2 style='font-size:18px;'>Here are your news updates:</h2><br/><br/>"

    # Load and add techsci news
    for category in techsci_categories:
        # Load the relevant techsci data
        current_date = datetime.now().strftime("%Y-%m-%d")
        filename = os.path.join(techsci_directory, f"{current_date}-{category}-news.json")
        with open(filename, "r") as f:
            data_techsci = json.load(f)

        message += f"<h3 style='font-size:18px;'>{category.title()} News:</h3><br/>"
        for article in data_techsci.get('articles', []):
            message += f"<p style='font-size:16px;'><b style='font-size:18px;'>Title:</b> {article['title']}<br/>"
            message += f"<b style='font-size:16px;'>Description:</b> {article['description']}<br/>"
            message += f"<b style='font-size:14px;'>Link:</b> <a href='{article['url']}'>Link to news article</a></p>"
            message += '<hr/>'  # Line separator

    # Load and add regional news
    for region in regions:
        # Load the relevant regional data
        current_date = datetime.now().strftime("%Y-%m-%d")
        filename = os.path.join(regional_directory, f"{current_date}-{region}-regional-news.json")
        with open(filename, "r") as f:
            data_regional = json.load(f)

        # Create lists to hold each category of regional news
        categories = {
            "political": [],
            "business and economy": [],
            "general": []  # Assuming all remaining articles fall under "General"
        }

        # Add regional news to relevant lists
        for article in data_regional.get('articles', []):
            category = article['category'].lower()
            if category in categories:
                news_item = f"<p style='font-size:16px;'><b style='font-size:18px;'>Country:</b> {article['country']}<br/>"
                news_item += f"<b style='font-size:16px;'>Title:</b> {article['title']}<br/>"
                news_item += f"<b style='font-size:16px;'>Description:</b> {article['description']}<br/>"
                news_item += f"<b style='font-size:14px;'>Link:</b> <a href='{article['url']}'>Link to news article</a></p>"
                news_item += '<hr/>'  # Line separator
                categories[category].append(news_item)

        # Add each category of news to the message
        for category, news_items in categories.items():
            message += f"<h3 style='font-size:18px;'>{region.upper()} {category.title()} News:</h3><br/>"
            message += ''.join(news_items)

    return message


def generate_message(regions, regional_directory, techsci_categories, techsci_directory):
    message = "<h2 style='font-size:18px;'>Here are your news updates:</h2><br/><br/>"

    # Load and add techsci news
    for category in techsci_categories:
        # Load the relevant techsci data
        current_date = datetime.now().strftime("%Y-%m-%d")
        filename = os.path.join(techsci_directory, f"{current_date}-{category}-news.json")
        with open(filename, "r") as f:
            data_techsci = json.load(f)

        message += f"<h3 style='font-size:18px;'>{category.title()} News:</h3><br/>"
        for article in data_techsci.get('articles', []):
            message += f"<p style='font-size:16px;'><b style='font-size:18px;'>Title:</b> {article['title']}<br/>"
            message += f"<b style='font-size:16px;'>Description:</b> {article['description']}<br/>"
            message += f"<b style='font-size:14px;'>Link:</b> <a href='{article['url']}'>Link to news article</a></p>"
            message += '<hr/>'  # Line separator

    # Load and add regional news
    for region in regions:
        # Load the relevant regional data
        current_date = datetime.now().strftime("%Y-%m-%d")
        filename = os.path.join(regional_directory, f"{current_date}-{region}-regional-news.json")
        with open(filename, "r") as f:
            data_regional = json.load(f)

        message += f"<h3 style='font-size:18px;'>{region.upper()} News:</h3><br/>"
        for article in data_regional.get('articles', []):
            message += f"<p style='font-size:16px;'><b style='font-size:18px;'>Title:</b> {article['title']}<br/>"
            message += f"<b style='font-size:16px;'>Description:</b> {article['description']}<br/>"
            message += f"<b style='font-size:14px;'>Link:</b> <a href='{article['url']}'>Link to news article</a></p>"
            message += '<hr/>'  # Line separator

    return message