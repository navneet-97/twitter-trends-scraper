from dotenv import load_dotenv
import os

load_dotenv()

# MongoDB Configuration
MONGODB_URI = os.getenv('MONGODB_URI')
DATABASE_NAME = 'twitter_trends'
COLLECTION_NAME = 'trending_topics'

# ProxyMesh Configuration
PROXYMESH_USERNAME = os.getenv('PROXYMESH_USERNAME')
PROXYMESH_PASSWORD = os.getenv('PROXYMESH_PASSWORD')
PROXYMESH_HOST = 'us-ca.proxymesh.com:31280'

# Twitter Configuration
TWITTER_USERNAME = os.getenv('TWITTER_USERNAME')
TWITTER_PASSWORD = os.getenv('TWITTER_PASSWORD')