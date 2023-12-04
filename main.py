import random
import numpy as np
import pandas as pd  # type:ignore
from typing import List, Dict


# Set the seed value based on a specific date
seed_date = "2023-07-15"  # Use the desired date
salt = 300

seed = int(seed_date.replace("-", ""))
random.seed(seed + salt)
np.random.seed(seed + salt)


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
    try:
        # Get the list of emails
        email_list = load_email_list("list_member_emails.txt")
        excluded_emails = load_email_list("list_excluded_member_emails.txt")

        # Shuffle the email list based on the seed value
        random.shuffle(email_list)

        # Number of emails to exclude from sampling
        n_excluded_emails = 5  # Set the desired number of emails to exclude

        # Assign a weight of 0 to the last n excluded emails
        print("Excluded emails are:")
        # print([mask_email(email) for email in excluded_emails])
        print(excluded_emails)

        email_weights = set_emails_probabilities(email_list, excluded_emails)

        # Sample three emails randomly based on the weights
        num_emails_to_select = 3
        random_emails = select_random_emails(
            email_list, list(email_weights.values()), num_emails_to_select
        )

        # Print the randomly chosen emails
        print("Randomly", num_emails_to_select, "chosen emails:")
        for email in random_emails:
            print(email)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
