## Runtime Flags

Runtime flags provide a flexible way to tailor your usage to your specific needs. These flags allow you to control various aspects of the program's behavior, such as package installation, API key handling, etc...

## Index

- [Runtime Flags](#runtime-flags)
- [Index](#index)
    - [Global Flags](#global-flags)
    - [API Key Configuration Flags](#api-key-configuration-flags)
    - [Logger Configuration Flags](#logger-configuration-flags)
    - [UI Configuration Flags](#ui-configuration-flags)

<!--
| Flag | Description |
| ---- | ----------- |
-->

### Global Flags

| Flag             | Description                                                                                                                                                                                                                                    |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`-noWinget`**  | This flag prevents the script from automatically installing packages using `winget`. This is useful if you prefer to use a different package manager like `chocolatey` or if you have specific installation requirements.                      |
| **`-enDevToys`** | Enables a set of developer-oriented configuration options. These options can be toggled to provide additional insights and debugging tools. The specific features enabled by this flag may vary depending on the application's implementation. |

### API Key Configuration Flags

| Flag                    | Description                                                                                                                                                                                                                                                                                                           |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`-doNotSaveMyKey`**   | This flag disables the automatic saving of your decrypted API key to the `key.txt` file. If this flag is enabled and the `key.txt` file exists, it will be deleted.                                                                                                                                                   |
| **`-extraSecret`**      | Allows you to enter your API key password in the terminal. Although not needed, when used in conjunction with the `doNotSaveMyKey` flag, this flag allows you to enter your API key password in the terminal each time you run the script. This ensures that your key remains secure and is not stored in plain text. |
| **`-customDecryption`** | This flag allows you to specify a custom decryption method if your encrypted API key is not in the standard `AES256` format. This provides flexibility for users with specific encryption preferences.                                                                                                                |

### Logger Configuration Flags

| Flag                   | Description                                                                                                                             |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| **`-noLogger`**        | Completely disables logging. No logs will be generated, neither to the terminal nor to a file.                                          |
| **`-noLoggerShell`**   | Prevents logs from being displayed in the terminal. Logged data will still be saved to a file if the `doNotSaveLogger` flag is not set. |
| **`-doNotSaveLogger`** | Prevents logs from being saved to a file. Logs will only be displayed in the terminal if the `noLoggerShell` flag is not set.           |

### UI Configuration Flags

| Flag              | Description                                                                                                                                                                                                                                                                                          |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`-loggerInUI`** | Enables a small, integrated terminal-like display within the user interface to show real-time log messages. Please note that this flag will be ineffective if logging is completely disabled using the flags mentioned in the **[Logger Configuration Flags](#logger-configuration-flags)** section. |