## Securing Your Gemini API Key

### Introduction

The Gemini API unlocks powerful AI capabilities for your Python projects. However, safeguarding your API key is crucial for security. This guide will walk you through encrypting your key and integrating it seamlessly into your Python environment.

### Instructions

**Prerequisites:**

- For Windows users, the `gpg4win` tool is required. This script can attempt automatic installation through `winget` if it's available on your system. If `gpg4win` is already installed via `winget`, this step will be bypassed.

**Steps:**

1. **Obtain Your API Key:**

   - Log in to the Google AI Platform.
   - Navigate to your project's API Keys page.
   - Create a new API key or use an existing one.
   - **Important:** Ensure the API key has the necessary permissions to access the Gemini API.

2. **Prepare Your API Key File:**

   - Create a JSON file named `api_key.json` with the following structure:

   ```json
   {
     "GEMINI": "your_api_key",
     "GCLOUD": "your_google_cloud_api_key" // Optional, if you have a Google Cloud account
   }
   ```

   - Replace `your_api_key` with your actual Gemini API key.
   - If you don't have a Google Cloud account, set the `GCLOUD` key to `null`.

3. **Encrypt Your API Key File:**

   1. **Install `gpg`:** If you haven't already, install [`gpg`](https://gnupg.org/) on your system.
      For Windows users, you can use:

      ```powershell
      winget install --id gnuPG.Gpg4win
      ```

   2. **Encrypt the file:**
      ```bash
      gpg --symmetric --cipher-algo AES256 --output encrypted_api_key.gpg api_key.json
      ```

   **Using Other Encryption Tools:**

   You can not use other encryption tools in this environment by default. If you wish to do so, you can always modify the source code of our API key manager in: [`clownkey.py`](../.secrets/clownkey.py).

4. **Secure Key Storage:**

   - Move your API key under the folder named `.secrets` in the project directory if you haven't already.

5. **Run the Python Script:**

   - Execute `main.py`. At first, the script will prompt you for the password used during encryption.
   - Once you enter the password, the script will decrypt your key and store a plain-text version of your password in `.secrets/key.txt` for future use.

   **Note:** You'll only be prompted for the password once. Subsequent script executions will automatically use the stored password in `.secrets/key.txt`.

This approach ensures secure storage of your sensitive API key while enabling seamless integration with your Python code.

**Customization:**

For advanced users who prefer to manage their API key differently, refer to the [`runtime_flags.md`](./runtime_flags.md) document for alternative configuration options.
