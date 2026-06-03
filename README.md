> [!NOTE] <br />
> *This project is IN PROGRESS and is done by Zsofia A. Palotas*
# Summary
**Automatization pipeline for customer data validation**<br />
The aim of this Python program is to validate customer's Tax Identification Number based on the pdf description provided by the countries and published on the OECD website.<br />
The final program will be containerized using Docker.
<br />
- Processes the TIN description documents with Gemini's API 
- Creates a regex from the rules described in the documents
- Processes the customer database (Excel/CSV)
- Validates each TIN if it matches a country's rule
- Flags invalid TINs in a new CSV

# Current state
So far...<br />
- The program can detect changes in the documents and update its database.<br />
- Embeddings are stored for development purposes<br />
- A list of regexes are created for all possible variations in a certain country's TIN structures.<br />
- The customer CSV is read and each person's TIN is validated against all the possible countries (no cleaning or input validation happens as of now)<br />

## Planned improvements
- Clean CSV and validate its fields
- Update CSV with result of accepting or rejecting the TIN
- Periodically check the OECD website for updates
- Containerize with Docker

# Instructions
Rename the .env.example -> .env<br />
Provide your own Gemini API key<br />
run: python3 data_extraction.py

## Notes
OECD website: https://www.oecd.org/en/networks/global-forum-tax-transparency/resources/aeoi-implementation-portal/tax-identification-numbers.html

# AI useage
Data extraction is done by following this guide: https://www.youtube.com/watch?v=EFUE4DHiAPM <br />
AI was only used to explain concepts and advise on implementation