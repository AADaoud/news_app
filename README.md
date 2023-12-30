This is a cool little news app project that uses News API, OpenAI API, and Google Cloud translate to gather recent news, and create a live feed of articles with images, descriptions, and flags to indicate the language of the news.

It uses a python flask backend and a react frontend which are dockerized and initiated using docker-compose and the .YAML file. It also can send reports in the form of a pdf to your email directly using GC Gmail api.

It takes information in any language and always displays it in one of English, Arabic, or Turkish.

Countries, language, and any of the backend logic can be changed by directly changing the variables found in the main.py file of the backend.

You can contact me for any questions.

Note: The API endpoints of OpenAI have previously changed which can cause the code to break. As of the time of creating this project the OpenAI endpoints are at chat/completion.
