## Runtime Flags

Runtime flags provide a flexible way to tailor your usage to your specific needs. These flags allow you to control various aspects of the program's behavior, such as package installation, API key handling, etc... If a flag is not used or set, the default value of this flag will be used instead.

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

| Flag                     | Description                                                                                                                                                                                                                                    | Default value |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------- |
| **`-noWinget`**          | This flag prevents the script from automatically installing packages using `winget`. This is useful if you prefer to use a different package manager like `chocolatey` or if you have specific installation requirements.                      | `False`       |
| **`-devToys`**           | Enables a set of developer-oriented configuration options. These options can be toggled to provide additional insights and debugging tools. The specific features enabled by this flag may vary depending on the application's implementation. | `False`       |
| **`-lactoseIntolerant`** | Suppresses `icecream` log messages (those starting with `ic \| ...`) from appearing in the terminal.                                                                                                                                           | `False`       |

### API Key Configuration Flags

| Flag                  | Description                                                                                                                                                                                                                                                                                                                                      | Default value |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------- |
| **`-doNotSaveMyKey`** | This flag disables the automatic saving of your decrypted API key password. If this flag is enabled and the `password.txt` file exists, it will be deleted.                                                                                                                                                                                      | `False`       |
| **`-extraSecret`**    | Allows you to enter your API key password in the terminal. Although not needed, when used in conjunction with the `-doNotSaveMyKey` flag, this flag allows you to enter your API key password in the terminal each time you run the script. This ensures that your key remains secure and is not stored in plain text anywhere in your computer. | `"str"`       |

### Logger Configuration Flags

| Flag                   | Description                                                                                                                                       | Default value |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ------------- |
| **`-noLogger`**        | Disables logging. No log entries will be generated for the terminal or saved to a file, streamlining output and file storage.                     | `False`       |
| **`-loggerShell`**     | Prevents logs from being displayed in the terminal. Logged data will only be saved to a file if the `noSaveLogger` flag is not set.               | `False`       |
| **`-noSaveLogger`**    | Prevents logs from being saved to a file. Logs will only be displayed in the terminal if the `loggerShell` flag is set.                           | `False`       |
| **`-loggerMaxBackup`** | Specifies the maximum number of log files to retain in the logger directory. Older files will be automatically removed when the limit is reached. | `5`           |
| **`-loggerName`**      | Specifies the logger name.                                                                                                                        | Current date  |

### UI Configuration Flags

| Flag                | Description                                                                                                                                                                                                                                                                               | Default value |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------- |
| **`-noLoggerInUI`** | Disables the integrated terminal-like display within the user interface for real-time log messages, providing a cleaner UI experience. Logging can still function in the terminal or in files if configured in the **[Logger Configuration Flags](#logger-configuration-flags)** section. | `True`        |
