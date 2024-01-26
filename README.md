# Swap File Management Tool (swap_bot) 🔄

The Swap File Management Tool, also known as swap_bot, is a simple Python program with a graphical user interface (GUI) that allows you to create, manage, and delete swap files on a BTRFS file system. This tool enables users to adjust the size of swap files, change swappiness settings, set priorities for swap files, and more.

## Features 🛠️

- Create and activate swap files on a BTRFS file system.
- Resize existing swap files.
- Customize swappiness (0-100) and swap file priorities (1-32768).
- Enable automatic priority settings.
- Delete selected swap files.
- View information about swappiness and priority settings.

## Requirements 📋

To use this tool, make sure the following requirements are met:

- A BTRFS file system is available.
- You have sudo privileges on your system.
- Python and the Tkinter library are installed on your system.

## Usage 🚀

1. Launch the tool by running the Python script `main.py`.

2. Select a folder on your BTRFS file system where the swap file should be created.

3. Enter the desired size of the swap file in megabytes (MB).

4. Adjust the swappiness (0-100) and priority (1-32768) settings for the swap file, or enable automatic priority settings.

5. Click the "Create and Activate Swap" button to create and activate the swap file.

6. You can select swap files from the list of existing ones and delete them using the "Delete Selected Swap Files" button.

## Note 📝

- Swappiness settings influence how aggressively the system swaps memory pages to the swap partition. Lower swappiness (e.g., 10) prevents swapping as much as possible, while higher swappiness (e.g., 100) causes the system to swap memory pages more frequently.

- The priority setting determines the order in which swap areas are used. Lower priority (e.g., 1) gives the swap partition a higher priority, while higher priority (e.g., 32768) treats it with lower priority.

## License 📄

This tool is released under the MIT License. For more details, see the [License file](LICENSE).

## Authors 🧑‍💻

This tool was developed by Hendrik Kaiser and utilizes ChatGPT, an AI model by OpenAI, for development and support.

## Support 📞

For any questions or issues, please reach out to [Your Contact Information].
