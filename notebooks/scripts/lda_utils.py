import nltk
import pandas as pd
import numpy as np

from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import GridSearchCV
from typing import Dict, List, Tuple, Union
from scipy.sparse._csr import csr_matrix
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from collections import Counter
from wordcloud import WordCloud


def clean_text(message: str) -> str:
    stop_words = set(nltk.corpus.stopwords.words("english"))

    lemmatizer = WordNetLemmatizer()
    word_tokens  = word_tokenize(message)
    tokens = [lemmatizer.lemmatize(token) for token in word_tokens
                if token not in stop_words]
    cleaned_text = " ".join(tokens)

    return cleaned_text

def perform_grid_search(
    search_params: Dict[str, List[Union[int, float]]], 
    vect_text: csr_matrix
) -> LatentDirichletAllocation:
    
    lda = LatentDirichletAllocation(
        batch_size=128, 
        learning_method="online", 
        max_iter=10, n_jobs=1, 
        evaluate_every=1,
        random_state=42
    )

    model = GridSearchCV(cv=None, error_score="raise", estimator=lda, param_grid=search_params)
    model.fit(vect_text)
    return model

def calculate_perplexities(search_params: Dict[str, List[Union[int, float]]], vect_text: csr_matrix) -> List[Dict[str, Union[int, float]]]:
    models = []
    components = search_params.get("n_components")
    l_rates = search_params.get("learning_decay")
    
    for component in components:
        for l_rate in l_rates:
            lda = LatentDirichletAllocation(
                n_components=component, 
                max_iter=10, 
                n_jobs=1, 
                evaluate_every=1, 
                learning_decay=l_rate,
                random_state=42
            )
            lda.fit_transform(vect_text)
            perplexity = lda.perplexity(vect_text)
            
            model = {"param_n_components": component, "param_learning_decay": l_rate, "perplexity": perplexity}
            models.append(model)
    
    return models

def extract_dominant_topics(
        model: LatentDirichletAllocation, 
        data: List[str],
        lda_output: np.ndarray

    ) -> pd.DataFrame:
    
    topics = [f"Topic {str(topic)}" for topic in range(model.n_components)]
    documents = [f"Document {str(index)}" for index, _ in enumerate(data)]
    document_lengths = [len(document) for document in data]

    df_document_topic = pd.DataFrame((np.round(lda_output, 2) * 100), columns=topics, index=documents)
    dominant_topic = np.argmax(df_document_topic.values, axis=1)
    
    df_document_topic["dominant_topic"] = dominant_topic
    df_document_topic["document_lengths"] = document_lengths

    return df_document_topic

def create_cat_dataframe(topic_dataframe: pd.DataFrame, total: int) -> Tuple[List[str], List[int]]:
    topics = topic_dataframe["dominant_topic"].to_list()
    counter = Counter(topics)
    cols = []
    quantities = []
    percentages = []

    for key, value in counter.items():
        cols.append(f"Topic {key}")

        curr_quantity = value
        curr_percentage = np.round((value / total), decimals=4) * 100

        quantities.append(value)
        percentages.append(curr_percentage)

    df = pd.DataFrame([quantities, percentages], columns=cols)

    return (df, cols, counter.values())


def generate_wordcloud(
    index: int, 
    model: LatentDirichletAllocation,
    vocab: np.ndarray
) -> WordCloud:
    
    words_topic = ""
    component = model.components_[index]
    vocabulary_components = zip(vocab, component)
    sorted_words = sorted(vocabulary_components, key=lambda x:x[1], reverse=True)[:50]

    for word in sorted_words:
        words_topic = words_topic + " " + word[0]
    
    wordcloud = WordCloud(background_color="white", width=600, height=400, max_words=8, colormap="plasma")
    wordcloud.generate(words_topic)

    return wordcloud

