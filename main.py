"""
Approach:
- Parse company names and URLs from input file
- Optionally scrape site text for additional grounding (limited)
- Query Gemini LLM with strict prompt to extract founders
- Save results in JSON format
"""
import re
import os
import requests
import json
from bs4 import BeautifulSoup
import google.generativeai as genai

#LLM setup
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

"""
A helper function to parse company names and URLs from a text file.
Returns: dict {company_name: url}
"""
def parse_companies(file_path):
    companies = {}
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            match = re.match(r"([A-Za-z0-9\s&.,'-]+)\s*\((https?://[^\)]+)\)", line)
            if match:
                name, url = match.groups()
                companies[name.strip()] = url.strip()
    return companies


def scrape_text(url, max_chars=3000):
    """Scrape raw text from a website to ground LLM responses. If allotted more time would be useful to be able to 
        crawl through website to find 'About', 'Meet the team', etc. pages and extract info from there to feed into llm."""
    try:
        html = requests.get(url, timeout=8).text
        soup = BeautifulSoup(html, "html.parser")
        #look for specific html tags that may contain founder titles
        texts = [t.get_text(" ", strip=True) for t in soup.find_all(["p", "h1", "h2", "h3"])]
        combined = " ".join(texts)
        return combined[:max_chars] # avoids overly large llm promopt
    except Exception as e:
        return ""

def ask_llm(company, url, context=None):
    """
    Ask Gemini for founders.
    We try to provide scraped site text as additional context. If not available, prompt without it.
    Always force strict JSON output for formatting.
    """
    if context:
        prompt = f"""
        Company: {company}
        Website text snippet:
        {context}

        Task: Extract ONLY the founders or co-founders of {company} : {url}.
        Rules:
        - Output must be a valid JSON array of strings (e.g., ["Alice Smith", "Bob Lee"])
        - Include only founders/co-founders (no advisors, no employees, no investors).
        """
    else:
        prompt = f"""
        Return ONLY the founders or co-founders of {company}.
        Rules:
        - Output must be a valid JSON array of strings.
        - Example: ["Brian Chesky", "Joe Gebbia", "Nathan Blecharczyk"]
        - No extra text, no explanations.
        """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error: {e}"

def main():
    # Begin by parsing companies from input file
    companies = parse_companies("companies.txt")
    results = {}
    for company, url in companies.items():
        # Attempt Scraping
        context = scrape_text(url)
        # Query LLM with context, if available
        founders = ask_llm(company, url, context if context else None)

        try:
            # Try to parse as JSON directly
            parsed = json.loads(founders)
            if isinstance(parsed, list):
                founders = parsed
            else:
                founders = []
        except Exception:
            # Fallback: regex to extract name-like patterns
            matches = re.findall(r"[A-Z][a-z]+\s[A-Z][a-z]+", founders)
            founders = list(set(matches))

        results[company] = founders

    # Save to file
    with open("founders.json", "w") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    main()