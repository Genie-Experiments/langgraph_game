from langchain_groq import ChatGroq
from dotenv import load_dotenv, find_dotenv
load_dotenv()


_ = load_dotenv(find_dotenv())
model = ChatGroq(model="llama3-8b-8192")