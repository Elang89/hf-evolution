import pandas as pd


def merge_issues_comments(issues: pd.DataFrame, comments: pd.DataFrame) -> pd.DataFrame:
    cols = ["timestamp", "document"]
    documents = []

    for _, row in issues.iterrows():
        description = row["issue_description"]
        title = row["issue_title"]
        timestamp = row["issue_timestamp"]

        if title:
            curr_val_title = [timestamp, title]
            documents.append(curr_val_title)

        if description:
            curr_val_body = [timestamp, description]
            documents.append(curr_val_body)

    for _, row in comments.iterrows():
        body = row["issue_comment_body"]
        timestamp = row["issue_comment_timestamp"]

        if body:
            curr_val = [timestamp, body]

            documents.append(curr_val)

    return pd.DataFrame(documents, columns=cols)