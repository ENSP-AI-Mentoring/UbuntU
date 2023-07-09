import random
import numpy as np
import pandas as pd #type:ignore

# Set the seed value based on a specific date
seed_date = '2023-07-15'  # Use the desired date
salt = 300

seed = int(seed_date.replace('-', ''))
random.seed(seed + salt)
np.random.seed(seed + salt)



def load_email_list(file_path):
    try:
        emails = pd.read_csv(file_path)
        email_list = emails['emails'].values
        return email_list
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error loading email list: {e}")


def set_emails_probabilities(email_list, excluded_emails):
    email_list_usable = [email for email in email_list if email not in excluded_emails]
    n = len(email_list_usable)
    print(f"There are {n} usable candidates out of {len(email_list)} total.")
    # Uniform probability distribution
    email_weights = [0 if email in excluded_emails else 1 / n for email in email_list]
    return email_weights


def select_random_emails(email_list, email_weights, num_emails):
    random_emails = np.random.choice(a=email_list, p=email_weights, size=num_emails, replace=False)
    return random_emails

def mask_email(email):
    # Split the email address into username and domain parts
    username, domain = email.split('@')

    # Calculate the number of characters to mask
    mask_length = int(len(username) * 0.68)

    # Mask the characters after the specified length
    masked_username = username[:mask_length] + '*' * (len(username) - mask_length)

    # Combine the masked username and domain to form the masked email
    masked_email = masked_username + '@' + domain

    return masked_email

def main():
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
        #print([mask_email(email) for email in excluded_emails])
        print(excluded_emails)

        email_weights = set_emails_probabilities(email_list, excluded_emails)

        # Sample three emails randomly based on the weights
        num_emails_to_select = 3
        random_emails = select_random_emails(email_list, email_weights, num_emails_to_select)

        # Print the randomly chosen emails
        print("Randomly",num_emails_to_select,"chosen emails:")
        for email in random_emails:
            print(email)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
