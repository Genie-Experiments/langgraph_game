import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))

model = ChatOpenAI(
    temperature=temperature,
    model_name=model_name,
    api_key=api_key
)

# from langchain_groq import ChatGroq
# from dotenv import load_dotenv, find_dotenv
# load_dotenv()
#
#
# _ = load_dotenv(find_dotenv())
# model = ChatGroq(model="llama3-8b-8192")