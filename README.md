
# Ubuntu

This GitHub Actions workflow is designed to select random members for certain activities based on specified criteria. It runs automatically on a schedule and can also be triggered manually.

## Scheduled Execution

The workflow is scheduled to run every Monday at 10:42 AM (UTC) using a cron expression `'42 10 * * mon'`. You can adjust the cron schedule as needed by modifying the `github-actions.yml` file.

## Manual Trigger

Additionally, you can manually trigger this workflow as needed. To manually trigger the workflow:

1. Navigate to the "Actions" tab in your GitHub repository.
2. Click on the "Pick_some_member" workflow.
3. Click the "Run workflow" button.
4. Provide any required input or parameters if prompted.

## Workflow Steps

The workflow consists of the following steps:

1. **Checkout Repository**: This step checks out your GitHub repository, allowing access to your code and workflow files.

2. **Setup Python**: It sets up a Python environment with version 3.8.

3. **Install Dependencies**: Installs the `numpy` and `pandas` Python packages using `pip`. Make sure you have listed these dependencies in your `pyproject.toml` or `requirements.txt` if they are required by your project.

4. **Run `main.py`**: Executes the `main.py` script, which performs various tasks related to selecting random members for activities based on criteria like last participation and eligibility.

5. **Create Team Sync Issue**: This step creates a GitHub issue titled "Team sync" with specified details. It assigns the issue to specific users (`hafro05` and `nprime496`) and adds labels (`weekly sync` and `docs-team`). The issue body contains a message inviting users to contribute.

## `main.py` Script

The heart of this workflow is the `main.py` script. It performs the following main tasks:

- Converts a Google Sheets URL to a CSV export URL.
- Fetches member data from the Google Sheet.
- Loads and retrieves a list of emails from a CSV file.
- Assigns probabilities to emails based on exclusions.
- Selects random emails based on assigned probabilities.
- Masks email addresses for privacy.

You can further customize the logic in the `main.py` script to meet your specific requirements.

## Usage

To use this GitHub Actions workflow for your project:

1. Create a copy of the `github-actions.yml` file in your repository.

2. Customize the cron schedule, job steps, and any other parameters to fit your project's needs.

3. Ensure that your Python code in `main.py` and any required dependencies are correctly set up and configured.

4. Configure any necessary secrets or environment variables in your GitHub repository settings.

5. Trigger the workflow manually or wait for the scheduled execution to begin.

Feel free to modify and extend this workflow to suit your project's requirements.


