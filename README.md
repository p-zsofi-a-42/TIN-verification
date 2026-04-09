> [!NOTE] <br />
> *This project is IN PROGRESS and is done by Zsofia A. Palotas*
# Summary
The aim of this Python program is to validate customer's Tax Identification Number based on the pdf description provided by the countries and published on the OECD website.<br />
The final program will be containerized using Docker.
<br />
- The pipeline checks for updates on the OECD website
- Processes the descriptions with Gemini's API 
- Creates a regex from the rules
- Processes the customer database (Excel/CSV)
- Validates each TIN if it matches a country's rule
- Flags invalid TINs in a new CSV

# Current state
So far the program can detect if a document was already processed<br />
If it's new, it processes and creates the regex for a provided and hard coded document.

# Instructions
Rename the .env.example -> .env<br />
Provide your own Gemini API key<br />
run: python3 data_extraction.py

## Notes
OECD website: https://www.oecd.org/en/networks/global-forum-tax-transparency/resources/aeoi-implementation-portal/tax-identification-numbers.html

# AI useage
Data extraction is done by following this guide: https://www.youtube.com/watch?v=EFUE4DHiAPM <br />
AI was only used to explain concepts and advise on implerentation