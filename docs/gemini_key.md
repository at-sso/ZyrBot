## Securing Your Gemini API Key

### Introduction

The Gemini API unlocks powerful AI capabilities for your Python projects. However, safeguarding your API key is crucial for security. This guide will walk you through encrypting your key and integrating it seamlessly into your Python environment.

### Instructions

**Prerequisites:**

- For Windows users, the `gpg4win` tool is required. This script can attempt automatic installation through `winget` if it's available on your system. If `gpg4win` is already installed via `winget`, this step will be bypassed.

**Steps:**

1. **Secure Key Storage:**

   - Under the folder named `.secrets` in the project directory.
   - Inside `.secrets`, create a file named `key.gpg`. This file will hold your encrypted API key.

2. **Encrypt Your API Key:**

   - Acquire your Gemini API key from the Google AI Platform.
   - Use a tool like `gpg4win` to encrypt your API key (as raw text) with the `AES256` algorithm. Here's an example command:

   ```sh
   gpg --symmetric --batch --cipher-algo AES256 --output key.gpg your_api_key.txt
   ```

   **Remember to replace `your_api_key.txt` with the actual path to your API key.**

3. **Run the Python Script:**

   - Execute `main.py`. At first, the script will prompt you for the password used during encryption.
   - Once you enter the password, the script will decrypt your key and store a plain-text version in `.secrets/key.txt` for future use.

   **Note:** You'll only be prompted for the password once. Subsequent script executions will automatically use the stored key in `.secrets/key.txt`.

This approach ensures secure storage of your sensitive API key while enabling seamless integration with your Python code.

**Customization:**

For advanced users who prefer to manage their API key differently, refer to the [`runtime_flags.md`](./runtime_flags.md) document for alternative configuration options.
