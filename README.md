# Gang Indictment RAG Pipeline

## Quick Start

1. **Clone the repo and navigate to the project folder:**

```bash
   git clone https://github.com/nizoom/GangIndictments
   cd GANGINDICTMENTS
```

2. **Create and activate a virtual environment:**

```bash
   python -m venv venv
   source venv/bin/activate        # Mac/Linux
   venv\Scripts\activate           # Windows
```

3. **Install dependencies:**

```bash
   pip install -r requirements.txt
```

4. **Set up your environment variables:**
   Create a `.env` file in the project root and add your Portkey API key:

```
   PORTKEY_API_KEY=your_key_here
```

5. **Open the notebook:**

```bash
   jupyter notebook rag.ipynb
```

## Overview

This project builds a Retrieval-Augmented Generation (RAG) pipeline over a collection of press releases published by New York District Attorneys regarding gang indictments. The goal is to extract structured, queryable data from unstructured legal documents — making it easier to analyze patterns in gang-related prosecutions across NYC boroughs. This notebook serves as a starting foundation for hackathon participants to explore and extend in any direction.

---

## Data Sources

- **Source**: NYC District Attorney press releases — public data
  - PDF documents covering gang indictment announcements from Brooklyn and other NYC boroughs
  - Example: `8_29_24_9Trey.pdf` (Brooklyn, August 2024)
  - Press releases are publicly available on the respective [DA office websites](https://www.brooklynda.org/)

---

## Data Processing & Cleaning

The pipeline processes raw PDF press releases and extracts structured fields using an LLM.

1. **PDF Text Extraction**: Full text is extracted from each PDF using `pdfplumber`, concatenating content across all pages.
2. **LLM-Based Field Extraction**: The extracted text is passed to `gpt-4o-mini` via Portkey, which returns a structured JSON object containing key fields from the press release.
3. **Geocoding Placeholder**: Location coordinates are set to `null` at extraction time and are intended to be geocoded in a subsequent step.

---

## Data Structure

The pipeline is organized as follows:

- `pdfs/`: Folder containing DA press release PDFs organized by borough.
  - `Brooklyn_Indictments/`: PDF press releases for Brooklyn indictments.
    - e.g., `8_29_24_9Trey.pdf`: Press release for a 9 Trey gang indictment, August 2024.
- `notebook.ipynb`: The main Python notebook containing the full pipeline — PDF ingestion, LLM extraction, and JSON output.

---

## Data Dictionary

The LLM extracts the following fields from each press release into a structured JSON object:

| Field              | Description                                                                             | Notes                                         |
| :----------------- | :-------------------------------------------------------------------------------------- | :-------------------------------------------- |
| `release_date`     | Date the press release was published                                                    |                                               |
| `borough`          | NYC borough associated with the indictment                                              |                                               |
| `da_name`          | Name of the District Attorney                                                           |                                               |
| `case_summary`     | 1–2 sentence summary of the case                                                        |                                               |
| `gangs_involved`   | List of gang names referenced                                                           | Empty list if none found                      |
| `defendants`       | List of defendants with name, age, aliases, and gang affiliation                        |                                               |
| `charges`          | List of unique charges mentioned in the release                                         |                                               |
| `incidents`        | List of incidents with date, location, and description                                  |                                               |
| `locations`        | List of locations with address, zip code, precinct, neighborhood, type, and coordinates | Coordinates set to `null` for later geocoding |
| `gang_territories` | List of gang territories with gang name and description                                 |                                               |

---

## Use Cases and Inspiration

1. **Geographic Mapping**: Geocode the extracted locations and build an interactive map of gang activity and incidents across NYC neighborhoods.
2. **Prosecution Pattern Analysis**: Analyze trends in charges, gang affiliations, and indictment frequency over time and across boroughs.
3. **Natural Language Q&A**: Extend the RAG pipeline into a chat interface where users can ask plain-English questions about the indictment data (e.g., "Which gangs were most active in Brooklyn in 2024?").
