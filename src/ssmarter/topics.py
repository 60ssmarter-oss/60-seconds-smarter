import random
from .utils import load_json

def choose_topic(path="data/topics.json"):
    topics = load_json(path)
    return random.choice(topics)
