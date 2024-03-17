from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


SIMILARITY_THRESHOLD = 0.7


def preprocess(text) -> str:
    """Lower and remove non-alphanumeric characters from text"""
    text = text.lower()
    text = [t for t in text.split() if t.isalnum()]
    return " ".join(text)


def get_similarity_scores(existing: list[str], new: str) -> np.array:
    """Calculates cosine similarity of existing text and new text"""
    vectorizer = CountVectorizer()
    vectorizer.fit(existing + [new])
    existing_vec = vectorizer.transform(existing)
    new_vec = vectorizer.transform([new])
    return cosine_similarity(existing_vec, new_vec)


def get_similar_tasks(existing_tasks: list[dict], new_task: dict) -> list[dict]:
    """
    This function calculates cosine similarity between existing titles/descriptions and new title/description.
    It returns similar results that at least reach the similarity threshold.
    For more accurate results the threshold can be increased.

    :param existing_tasks: list of dictionaries of existing tasks
    :param new_task: dictionary of new task
    :return: list of dictionaries of top five similar tasks
    """
    existing_titles = [preprocess(task["title"]) for task in existing_tasks]
    new_title = preprocess(new_task["title"])

    existing_descriptions = [preprocess(task["description"]) for task in existing_tasks]
    new_description = preprocess(new_task["description"])

    title_similarity_scores = get_similarity_scores(existing_titles, new_title)
    description_similarity_scores = get_similarity_scores(
        existing_descriptions, new_description
    )

    total_similarity = (title_similarity_scores + description_similarity_scores) / 2
    similar_tasks = []
    for index, score in enumerate(total_similarity):
        if score >= SIMILARITY_THRESHOLD:
            similar_tasks.append(existing_tasks[index])

    return similar_tasks


# BELOW is unfinished code. I left this here to showcase the different approaches to the unique challange


# from nltk.tokenize import word_tokenize
# from nltk.stem import WordNetLemmatizer
# from mlxtend.frequent_patterns import apriori
# from mlxtend.preprocessing import TransactionEncoder
# import pandas as pd

# @router.get("/task/smart")
# async def get_smart_suggestion():
#     tasks = await database.fetch_all(tasks_table.select())
#     tasks = [{**task} for task in tasks]
#     data = [[f"{task['title'].lower()} {task['description'].lower()}"] for task in tasks]
#     tokens = [word_tokenize(datum[0]) for datum in data]
#     # stop_words = set(stopwords.words("english"))
#     # tokens = [[t for t in token if t not in stop_words] for token in tokens]
#     wnl = WordNetLemmatizer()
#     tokens = [[wnl.lemmatize(t) for t in token] for token in tokens]
#     #tokens = [[" ".join(token)] for token in tokens]
#     te = TransactionEncoder()
#     te_ary = te.fit(tokens).transform(tokens)
#     df = pd.DataFrame(te_ary, columns=te.columns_)
#     r = apriori(df, min_support=0.6, use_colnames=True)
#     print('s')


# @router.get("/task/smart")
# async def get_smart_suggestion():
#     """
#     SELECT
#         *,
#         strftime('%Y', completed_ts) as year,
#         strftime('%m', completed_ts) as month,
#         strftime('%e', completed_ts) as day,
#
#     """
#     tasks = await database.fetch_all(tasks_table.select().order_by(tasks_table.c.completed_ts))
#     tasks = [{**task} for task in tasks]
#     seq = []
#     for i in range(1, len(tasks)):
#         time_difference: timedelta = tasks[i]['completed_ts'] - tasks[i - 1]['completed_ts']
#         if time_difference.seconds / 60 < 10:
#             seq.append()
#
#     await calculate_similarity(tasks)
#
#     return tasks

# from difflib import SequenceMatcher
# from typing import NamedTuple

# class Similarity(NamedTuple):
#     task_index: int
#     similarity_score: float
#
#
# async def calculate_similarity(tasks):
#     for i in range(len(tasks)):
#         task_i = tasks[i]
#         j = i + 1
#         similarities = []
#         while j <= len(tasks) - 1:
#             task_j = tasks[j]
#             title_similarity = SequenceMatcher(
#                 a=task_i["title"], b=task_j["title"]
#             ).ratio()
#             description_similarity = SequenceMatcher(
#                 a=task_i["description"], b=task_j["description"]
#             ).ratio()
#             total_similarity = (title_similarity + description_similarity) / 2
#             if total_similarity >= 0.7:
#                 similarity = Similarity(j, total_similarity)
#                 similarities.append(similarity)
#             j += 1
#         task_i.update({"similarities": similarities})


# when a new task is created calculate similarities and suggest new tasks
# when a task is set to completed check for similar completed task and
# see if there are any completed tasks in a short interval after and suggest them
