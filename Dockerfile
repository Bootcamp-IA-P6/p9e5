FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "\
import nltk; \
nltk.download('stopwords', quiet=True); \
nltk.download('wordnet', quiet=True); \
nltk.download('omw-1.4', quiet=True)"

RUN python -c "\
from transformers import pipeline; \
pipeline('text-classification', model='Gabriela-Her/p9e5-hate-speech-detector')"

COPY . .

EXPOSE 8501

CMD ["python", "-m", "streamlit", "run", "app/app.py", \
     "--server.address=0.0.0.0", \
     "--server.port=8501"]