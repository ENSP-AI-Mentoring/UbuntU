import random
import numpy as np
import pandas as pd  # type:ignore
from typing import List, Dict
import re
from datetime import date, datetime, timedelta
import os


def convert_google_sheet_url(url):
    """
        Function to convert Google Sheets URL into a CSV export URL
    """
    # Regular expression to match and capture the necessary part of the URL
    pattern = r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)(/edit#gid=(\d+)|/edit.*)?'

    # Replace function to construct the new URL for CSV export
    # If gid is present in the URL, it includes it in the export URL, otherwise, it's omitted
    replacement = lambda m: f'https://docs.google.com/spreadsheets/d/{m.group(1)}/export?' + (f'gid={m.group(3)}&' if m.group(3) else '') + 'format=csv'

    # Replace using regex
    new_url = re.sub(pattern, replacement, url)

    return new_url


def fetch_data(url, columns):
    """
        Function to fetch the information of the members

        Args:
        - url (str): CSV export URL of the Google Sheet containing the information to fetch
        - columns (List of str): list containing the columns of the Google Sheet to return

        Returns:
        - DataFrame containing the columns specified in argument

        Raises:
        - Exception: For any other unexpected errors during file reading.
    """
    new_url = convert_google_sheet_url(url)

    #read the data
    try:
        df = pd.read_csv(new_url)
        return df[columns].dropna()
    except Exception as e:
        print(f"Error when fetching the data: {e}")
        return None


def load_email_list(file_path: str) -> List[str]:
    """Load and retrieve a list of emails from a CSV file.

    Args:
    - file_path (str): The path to the CSV file containing email data.

    Returns:
    - List[str]: A list of email addresses extracted from the CSV file.

    Raises:
    - FileNotFoundError: If the specified file_path does not exist.
    - Exception: For any other unexpected errors during file reading.
    """
    try:
        emails = pd.read_csv(file_path)
        if "emails" in emails:
            email_list = emails["emails"].tolist()
            return email_list
        else:
            raise ValueError("Column 'emails' not found in the CSV file.")
    except FileNotFoundError as file_error:
        raise FileNotFoundError(f"File not found: {file_path}") from file_error
    except Exception as e:
        raise Exception(f"Error loading email list: {e}")


def set_emails_probabilities(
    email_list: List[str], excluded_emails: List[str]
) -> Dict[str, float]:
    """
    Assigns probabilities to emails in the list based on exclusions.

    Args:
    - email_list (List[str]): List of emails to assign probabilities to.
    - excluded_emails (List[str]): List of emails to be excluded from assignment.

    Returns:
    - Dict[str, float]: Dictionary containing emails as keys and assigned probabilities as values.
    """
    usable_emails = [email for email in email_list if email not in excluded_emails]
    n_usable = len(usable_emails)
    n_total = len(email_list)

    print(f"There are {n_usable} usable candidates out of {n_total} total.")

    # Assigning probabilities
    email_probabilities = {}
    if n_usable > 0:
        probability = 1 / n_usable
        for email in email_list:
            if email in usable_emails:
                email_probabilities[email] = probability
            else:
                email_probabilities[email] = 0

    return email_probabilities


def select_random_emails(
    email_list: List[str], email_weights: List[float], num_emails: int
) -> List[str]:
    """
    Selects a specified number of random emails from the provided list based on weights.

    Args:
    - email_list (List[str]): List of email addresses.
    - email_weights (List[float]): Weights associated with each email address.
    - num_emails (int): Number of emails to be selected.

    Returns:
    - List[str]: Randomly selected email addresses based on the provided weights.
    """
    random_emails = np.random.choice(
        a=email_list, p=email_weights, size=num_emails, replace=False
    )
    return random_emails.tolist()  # Converts numpy array to a Python list


def mask_email(email: str) -> str:
    """
    Masks the characters in the username of an email address for privacy purposes.

    Args:
    - email (str): The email address to be masked.

    Returns:
    - str: The masked email address with part of the username replaced by '*'.
    """

    # Split the email address into username and domain parts
    username, domain = email.split("@")

    # Calculate the number of characters to mask
    mask_length = int(len(username) * 0.68)

    # Mask the characters after the specified length
    masked_username = username[:mask_length] + "*" * (len(username) - mask_length)

    # Combine the masked username and domain to form the masked email
    masked_email = masked_username + "@" + domain

    return masked_email


def main() -> None:
    """
    main method.
    """
    # Set the seed value based on a specific date
    seed_date = "2023-07-15"  # Use the desired date
    salt = 300

    seed = int(datetime.now().timestamp())
    random.seed(seed + salt)
    np.random.seed(seed + salt)

    DELAY = 0.2 # Number of months after which we are included in the draw again afer a participation
    ACTIVITIES = ["presentation"] # ["presentation", "article"]
    NB_OF_MEMBERS_TO_DRAW = 1

    # Get the information of the members
    # Raw URL of the Google Sheet containing the information of the members
    members_sheet_url = "https://docs.google.com/spreadsheets/d/12iwGURrqjezAuqI96fv16skKExkFY5WBloX-2iIKL5g/edit#gid=0"
    personal_info_columns = ["emails", "github username"]

    participation_colmun_from_activity = lambda activity : f"{activity}_last_participation"
    activity_drawable_column = lambda activity : f"{activity}_drawable"

    participation_columns = [participation_colmun_from_activity(activity) for activity in ACTIVITIES]

    data = fetch_data(members_sheet_url, personal_info_columns+participation_columns)

    if data is not None: # Fetching the data succeeded
        for activity in ACTIVITIES:
            #create  a column to indicate if we can draw each person or not for the activity
            data[activity_drawable_column(activity)] = data[participation_colmun_from_activity(activity)].apply(lambda x: (datetime.now() - datetime.strptime(x, "%d/%m/%Y")) >= timedelta(days=DELAY*30))

            candidates_df = data[data[activity_drawable_column(activity)] == True]

            email_list = candidates_df["emails"].values

            # Shuffle the email list based on the seed value
            random.shuffle(email_list)

            # Choose the mails
            if len(email_list) > NB_OF_MEMBERS_TO_DRAW:
                choosed_emails = (np.random.choice(a=email_list, size=NB_OF_MEMBERS_TO_DRAW, replace=False)).tolist()
            else:
                choosed_emails = email_list

            # Get the associated github usernames of the selected emails
            selected_members = data[data["emails"].isin(choosed_emails)]
            selected_members_gh_usernames = selected_members["github username"].values

            # Write the selected usernames in the GITHUB_ENV environment
            env_file = os.getenv('GITHUB_ENV')
        
            with open(env_file, 'a') as file:
                for i, username in enumerate(selected_members_gh_usernames, start=1):
                    file.write(f"user{i}={username}\n")
                
if __name__ == "__main__":
    main()
