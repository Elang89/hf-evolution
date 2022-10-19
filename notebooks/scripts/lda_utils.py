import string
import pandas as pd
import numpy as np
import re
import spacy
import gensim
import gensim.corpora as corpora

from typing import Dict, List, Tuple, Generator
from nltk.corpus import stopwords
from collections import Counter
from wordcloud import WordCloud
from gensim.utils import simple_preprocess



def clean_text(dataframe: pd.DataFrame) -> List[List[str]]:
    nlp = spacy.load("en_core_web_sm")
    documents = dataframe["commit_message"].to_list()
    stop_words = stopwords.words("english")
    stop_words.extend(["mb", "et", "al", "use", "yml" "also", "md", "zip", "gcs", "com", "jsonl", "json",
    "http", "huggingtweet", "spm", "pth", "https", "sa", "cc", "py", "ab", "png", "jpg", "mp4", 
    "dataset", "datum", "information", "neededmore", "model", "huggingface", "txt", "pkl"])
    punctuation = set(string.punctuation)

    documents = [re.sub("\S*@\S*\s?", "", document) for document in documents]
    documents = [_remove_emojis(document) for document in documents]
    documents = list(_convert_to_words(documents))
    documents = [[word for word in document if word not in stop_words] for document in documents]
    documents = _lemmatize(documents, nlp)
    documents = [[word for word in document if word not in stop_words] for document in documents]

    return documents


def build_bigrams(documents: List[List[str]]) -> Tuple[List[List[str]], gensim.models.phrases.Phraser]:
    bigram = gensim.models.Phrases(documents, min_count=5, threshold=100)
    bigram_mod = gensim.models.phrases.Phraser(bigram)
    bigrams = [bigram_mod[document] for document in documents]

    return (bigrams, bigram_mod)

def build_trigrams(documents: List[List[str]], bigram: gensim.models.phrases.Phraser) -> List[List[str]]:
    trigram = gensim.models.Phrases(bigram[documents], threshold=100)
    trigram_mod = gensim.models.phrases.Phraser(trigram)
    trigrams = [trigram_mod[document] for document in documents]

    return trigrams


def create_model(documents: List[List[str]], num_topics: int) -> Tuple[
        List[List[str]], 
        corpora.Dictionary, 
        gensim.models.ldamodel.LdaModel
    ]:

    id2word = corpora.Dictionary(documents)
    corpus = [id2word.doc2bow(document) for document in documents]


    lda_model = gensim.models.ldamodel.LdaModel(
        corpus=corpus, id2word=id2word, num_topics=num_topics,
        chunksize=100, passes=100,
        per_word_topics=True
    )

    return (corpus, id2word, lda_model)


def _lemmatize(
    documents: List[List[str]],
    nlp: spacy.Language, 
    allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV'],
) -> List[List[str]]:
    resulting_docs = []

    for document in documents:
        new_doc = nlp(" ".join(document))
        tokens = [token.lemma_ for token in new_doc if token.pos_ in allowed_postags]
        resulting_docs.append(tokens)
    
    return resulting_docs

def _convert_to_words(documents: str) -> Generator[str, None, None]:
    for document in documents:
        yield simple_preprocess(document, deacc=True, min_len=3)


def extract_dominant_topics(
        model: gensim.models.LdaModel, 
        corpus: List[List[str]],
        documents: List[str],
        named_topics: Dict[int, str]
    ) -> pd.DataFrame:
    cols = ["Dataset", "Dominant Topic", "Percentage(%)"]
    values = []

    for index, topic_val in enumerate(model[corpus]):
        row = sorted(topic_val[0], key = lambda x: (x[1]), reverse=True)
        dominant_topic  = named_topics.get(row[0][0])
        dominant_topic_percentage = (row[0][1] * 100) 
        document = documents[index]

        values.append([document, dominant_topic, dominant_topic_percentage])
    
    return pd.DataFrame(values, columns=cols)


def clean_titles(title: str) -> str:
    new_title = title.strip()
    new_title = _remove_emojis(new_title)
    new_title = new_title.encode("ascii", errors="ignore")
    new_title = new_title.decode("ascii")
    new_title = re.sub(r"http\S+", "", new_title)

    if len(new_title) > 50:
        new_title = new_title[:20]

    return new_title



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
    model: gensim.models.LdaModel,
    topic: int,
    named_topics: Dict[int, str],
    max_words: int
) -> Tuple[str, WordCloud]:
    named_topic = named_topics.get(topic)
    words = model.show_topic(topic)
    text = {word: value for word, value in words}
    wordcloud = WordCloud(background_color="white", width=600, height=400, max_words=max_words, colormap="plasma")
    wordcloud.generate_from_frequencies(text)

    return (named_topic, wordcloud)


def create_tsne(model: gensim.models.LdaModel, corpus: List[List[int]]) -> Tuple[np.ndarray, np.ndarray]:
    topic_weights = []
    topics = model[corpus]

    for index, topic in enumerate(topics):
        weights = [weight for _, weight in topic[0]]
        topic_weights.append(weights)

    df_weights = pd.DataFrame(topic_weights).fillna(0).values
    df_weights = df_weights[np.amax(df_weights, axis=1) > 0.35]
    dominant_topics = np.argmax(df_weights, axis=1)

    return (df_weights, dominant_topics)


def _remove_emojis(document: str) -> str:
    emoj = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
                      "]+", re.UNICODE)
    
    return re.sub(emoj, "", document)

