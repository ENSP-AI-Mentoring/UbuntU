import random
import numpy as np
import pandas as pd  # type:ignore
from typing import List, Dict, Optional, Any, Union
import re
from datetime import datetime
import os

from dotenv import load_dotenv
import logging
import tempfile
import argparse

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()


def convert_google_sheet_url(url: str) -> str:
    """
    Function to convert Google Sheets URL into a CSV export URL
    """
    # Regular expression to match and capture the necessary part of the URL
    pattern = r"https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)(/edit#gid=(\d+)|/edit.*)?"

    # Replace function to construct the new URL for CSV export
    # If gid is present in the URL, it includes it in the export URL, otherwise, it's omitted
    def replacement(m: re.Match) -> str:
        """
        Convert a Google Sheets URL into a direct download link for a CSV file.

        This function takes a match object from a regular expression search, which
        contains groups capturing specific parts of a Google Sheets URL. It then
        constructs and returns a URL that directly downloads the sheet in CSV format.

        Parameters:
        m (re.Match): A match object containing groups from a regular expression
                    search. The first group should contain the Google Sheets ID,
                    and the third group (optional) should contain the 'gid' for
                    a specific sheet within the document.

        Returns:
        str: A URL string that provides a direct download link for the Google Sheet
            as a CSV file. The URL includes the sheet ID, and optionally, the 'gid'
            if it is specified in the match object.
        """
        return (
            f"https://docs.google.com/spreadsheets/d/{m.group(1)}/export?"
            + (f"gid={m.group(3)}&" if m.group(3) else "")
            + "format=csv"
        )

    # Replace using regex
    new_url = re.sub(pattern, replacement, url)

    return new_url


def fetch_data_from_url(url: str, columns: List[str]) -> Optional[pd.DataFrame]:
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

    logging.info(url)
    new_url = convert_google_sheet_url(url)

    # read the data
    try:
        df = pd.read_csv(new_url)
        df.columns = [col.lower().strip() for col in df.columns]
        df_trimmed = df[columns]
        df_trimmed_drop = df_trimmed.dropna(how="all", axis=0)
        return df_trimmed_drop
    except Exception as e:
        logging.error(f"Error when fetching the data: {e}")
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


# def set_probabilities(
#     item_list: List[str], excluded_items: List[str]
# ) -> Dict[str, float]:
#     """
#     Assigns probabilities to emails in the list based on exclusions.

#     Args:
#     - email_list (List[str]): List of emails to assign probabilities to.
#     - excluded_emails (List[str]): List of emails to be excluded from assignment.

#     Returns:
#     - Dict[str, float]: Dictionary containing emails as keys and assigned probabilities as values.
#     """
#     usable_emails = [email for email in item_list if email not in excluded_items]
#     n_usable = len(usable_emails)
#     n_total = len(item_list)

#     logging.info(f"There are {n_usable} usable candidates out of {n_total} total.")

#     # Assigning probabilities
#     email_probabilities = {}
#     if n_usable > 0:
#         probability = 1 / n_usable
#         for email in item_list:
#             if email in usable_emails:
#                 email_probabilities[email] = probability
#             else:
#                 email_probabilities[email] = 0

#     return email_probabilities


def random_choice_using_weights(
    items: List[str], k: int, item_weights: List[float]
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
    selected_items = np.random.choice(a=items, p=item_weights, size=k, replace=False)
    return selected_items.tolist()  # Converts numpy array to a Python list


# def mask_email(email: str) -> str:
#     """
#     Masks the characters in the username of an email address for privacy purposes.

#     Args:
#     - email (str): The email address to be masked.

#     Returns:
#     - str: The masked email address with part of the username replaced by '*'.
#     """

#     # Split the email address into username and domain parts
#     username, domain = email.split("@")

#     # Calculate the number of characters to mask
#     mask_length = int(len(username) * 0.68)

#     # Mask the characters after the specified length
#     masked_username = username[:mask_length] + "*" * (len(username) - mask_length)

#     # Combine the masked username and domain to form the masked email
#     masked_email = masked_username + "@" + domain

#     return masked_email


def main(
    members_sheet_url: str,
    number_of_members_to_draw: int,
    value_expected: str,
    column_to_check: str,
) -> None:
    """
    main method.
    """
    # Set the seed value based on a specific date
    # seed_date = "2023-07-15"  # Use the desired date
    salt = 300
    seed = int(datetime.now().timestamp())
    random.seed(seed + salt)
    np.random.seed(seed + salt)

    columns_of_interest = [IDENTIFIER_COLUMN, column_to_check]
    columns_of_interest = [col.lower().strip() for col in columns_of_interest]

    data = fetch_data_from_url(members_sheet_url, columns_of_interest)

    # logging.debug(d)

    def random_choice(items_list: Any, k: int = 1) -> Any:
        if len(items_list) > k:
            logging.debug(
                f"Number of items to select is equal to {k} and the number of items is {len(items_list)}"
            )
            selected_items = (
                np.random.choice(a=items_list, size=k, replace=False)
            ).tolist()

        else:
            selected_items = candidates_list
            logging.debug(
                f"Not or just enough items to select, number of items to select is equal to {k} and the number of items is {len(items_list)}"
            )
        return selected_items

    # def is_drawable(columns_to_check: List[str], values_expected: str) -> bool:
    #     """
    #     Function to check if a person is drawable for the current draw
    #     """
    #     return list(columns_to_check) == list(values_expected)

    if data is not None:  # Fetching the data succeeded
        # create  a column to indicate if we can draw each person or not for the activity
        candidates_df = data[
            data[column_to_check].apply(
                lambda x: str(x).lower() == str(value_expected).lower()
            )
        ]

        candidates_list = candidates_df[IDENTIFIER_COLUMN].values

        # Shuffle the identifiers list based on the seed value
        random.shuffle(candidates_list)

        # Choose the identifiers

        choosen_candidates = random_choice(
            items_list=candidates_list, k=number_of_members_to_draw
        )

        # # Get the associated github usernames of the selected emails
        # selected_members = data[data[IDENTIFIER_COLUMN].isin(choosen_candidates)]
        # selected_identifiers = selected_members[IDENTIFIER_COLUMN].values

        # Write the selected usernames in the GITHUB_ENV environment
        env_file = os.getenv("GITHUB_ENV")
        if env_file is None:
            # If GITHUB_ENV is not set, we are likely in dev env, use a temporary file
            with tempfile.NamedTemporaryFile(mode="a", delete=False) as file:
                for i, username in enumerate(choosen_candidates, start=1):
                    file.write(f"user{i}={username}\n")
        else:
            with open(env_file, "a") as file_env:
                for i, username in enumerate(choosen_candidates, start=1):
                    file_env.write(f"user{i}={username}\n")
    else:
        logging.error("No data fetched ! Aborting.")


if __name__ == "__main__":
    # TODO: Add support for csv file directly
    # TODO: Write list to env and iterate in message

    DELAY = 3  # Number of months after which we are included in the draw again afer a participation
    NB_OF_MEMBERS_TO_DRAW = 1

    parser = argparse.ArgumentParser(description="Member Selection Script")
    parser.add_argument("--seed_date", type=str, help="Seed date for randomness")
    parser.add_argument(
        "--delay", type=int, default=3, help="Delay in months for re-inclusion in draw"
    )
    parser.add_argument(
        "--number_of_members_to_draw",
        type=int,
        default=NB_OF_MEMBERS_TO_DRAW,
        help="Number of members to draw",
    )
    parser.add_argument(
        "--activities", nargs="+", default=["presentation"], help="List of activities"
    )
    parser.add_argument(
        "--members_sheet_url",
        type=str,
        # required=True,
        default=None,
        help="Google Sheet URL for member information",
    )

    parser.add_argument(
        "--column_to_check",
        type=str,
        required=True,
        default=[],
        help="Column to check against",
    )

    parser.add_argument(
        "--value_expected",
        type=str,
        # required=True,
        default=None,
        help="Value expected",
    )

    parser.add_argument(
        "--output_file", type=str, help="Output file for selected usernames"
    )

    args = vars(parser.parse_args())  # Converts to  dict

    members_sheet_url: str = ""

    if args["members_sheet_url"] is None:
        members_sheet_url = str(os.environ["MEMBERS_SHEET_URL"])
        logging.info("Defaulting to environment variable")
    else:
        members_sheet_url = args["members_sheet_url"]

    seed_date = args["seed_date"]
    delay = args["delay"]
    IDENTIFIER_COLUMN = "github_username"
    number_of_members_to_draw = args["number_of_members_to_draw"]
    activities = args["activities"]
    value_expected = args["value_expected"]
    if value_expected is None:
        value_expected = "AVAILABLE"
    column_to_check = args["column_to_check"]
    # members_sheet_url = args["members_sheet_url"]
    output_file = args["output_file"]
    # ACTIVITIES = ["presentation"]  # ["presentation", "article"]

    main(
        members_sheet_url=members_sheet_url,
        number_of_members_to_draw=number_of_members_to_draw,
        value_expected=value_expected,
        column_to_check=column_to_check,
    )
