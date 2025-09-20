import spacy
import pdfplumber
import re

file_path = 'pdfs/Queens Indictments/trap_stars_money_world_03_21_2023_ind_2.pdf'

def extract_text_from_pdf(file_path):
    full_text = ''
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"
    return full_text

raw_text = extract_text_from_pdf(file_path)

nlp = spacy.load("en_core_web_sm")
doc = nlp(raw_text)
def extract_defendant_data(text):
    data = {}

    # Dates
    match = re.search(r"\b(\d{1,2}\/\d{1,2}\/\d{2,4})\b", text)
    data["Date"] = match.group(1) if match else None

    # Borough (“Queens” in this PDF)
    boroughs = ["Queens", "Brooklyn", "Manhattan", "Bronx", "Staten Island"]
    for b in boroughs:
        if b in text:
            data["Borough"] = b
            break

    # DA name: look for headings like "Queens County District Attorney" then Person entity
    for sent in doc.sents:
        if "District Attorney" in sent.text:
            ents = [ent.text for ent in sent.ents if ent.label_ == "PERSON"]
            data["DA Name"] = ents[0] if ents else None
            break

    # Defendant details in lines (Name, Alias, Age, Area, Gang Subset, Precinct, Top Charge)
    pat = re.compile(
        r"Name:\s*(?P<Name>.+?)\s+Alias\(es\):\s*(?P<Aliases>.+?)\s+Age:\s*(?P<Age>\d+)"
        r"\s+Area:\s*(?P<Area>.+?)\s+Gang Subset:\s*(?P<Gang>.+?)\s+Precinct:\s*(?P<Precinct>\d+)"
        r"\s+Top Charge:\s*(?P<Charge>.+?)\s+Alleged Conduct:\s*(?P<Conduct>.+?)\s+Max Sentence:\s*(?P<Max>.+)"
        , re.DOTALL
    )

    match = pat.search(text)
    if match:
        data.update(match.groupdict())
    else:
        # fallback: search each field individually
        fields = ["Name", "Alias", "Age", "Area", "Gang Subset", "Precinct", "Top Charge", "Alleged Conduct", "Max Sentence"]
        for field in fields:
            pat2 = re.search(fr"{re.escape(field)}:\s*(.+)", text)
            data[field] = pat2.group(1).strip() if pat2 else None

    return data

info = extract_defendant_data(raw_text)
print(info)
