# mbox2db: Importing Mbox Data to MySQL

This Python script facilitates the import of email data from an mbox file into a MySQL database table using the pandas library.

**Key Features:**

* **Mbox to MySQL Import:** Parses and imports email content from standard mbox format files.
* **Append Functionality:** If the specified MySQL table already exists, the script appends the new email data to it, preserving existing records.

## Motivation

The primary motivation for developing this tool arose from the need to archive and analyze email data from various sources. Specifically, the initial use case involved migrating email archives from an infrequently used iCloud account, accessible via Thunderbird on a Linux system. Hosting these archives locally within a controlled database environment offers several advantages, including:

* **Local Data Management:** Eliminates reliance on external email service providers for long-term storage.
* **Spam Mitigation:** Provides a mechanism to consolidate and analyze spam emails for potential patterns.
* **Data Analysis Potential:** Enables the application of database querying and analytical techniques to the email content.

A particular area of interest lies in identifying potential connections between different email addresses and associated data, such as cryptocurrency wallet identifiers found within the email content. This analysis could provide insights into the prevalence and patterns of scam-related communications.

## Usagee

* $ uv run ./mbox2db.py

you will be promped for the location of the [table].mbox folder, it will parse the mbox file inside


## License

[The 3-Clause BSD License](https://opensource.org/license/bsd-3-clause)

SPDX short identifier: BSD-3-Clause