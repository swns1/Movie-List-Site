import requests
import os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")
URL = "https://api.themoviedb.org/3/search/movie"

class MovieApi:
    def __init__(self, title):
        self.params = {
            "api_key": API_KEY,
            "query": title
        }
        self.response = requests.get(URL, params=self.params)
        self.data = self.response.json()["results"]
