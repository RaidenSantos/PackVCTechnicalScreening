# PackVCTechnicalScreening
Take home technical exercise for PackVC. Created a tool that finds founder names given a text file of companies.

How to run solution:
1. Install dependencies: 
    - Navigate to project directory
    - pip install beautifulsoup4 requests google-generativeai
2. Set google API key
   - Navigate to: aistudio.google.com and get an api key
   - Set API key by running this command in terminal: export GOOGLE_API_KEY="your_api_key"
3. Run the script: python main.py companies.txt
4. Output will be saved in: founders.json


Approach and Assumptions: 
I explored multiple strategies to identify company founders:
1. Pure Web Scraping
    - I first tried a pure web scraping approach to identify company founders using beautiful soup to pull names
        directly from the html in company websites. 
    - Failed beacuse website structure varies widely. Some listed founders on the home page, others buried them under nested "About" or "Team" pages, or under hyperlinks. 
        Additionally some websites use dynamic content that is hard to parse. 
    - Trying to match keywords like "Founder" or "Co-Founder" pulled in unrelated roles or other fluff which would have required much more complex 
pattern matching. 
2.  LLM Only Approach
    - I also tried to query Gemini with company names and urls. While it worked correctly in the chat interface, when calling it from the API it would hallucinate names.
    - Especially true for smaller companies (like those listed on the PackVC website). I believe this is because the API doesn't have access to the internet to ground
        answers and get external context.
3. Scraping + LLM
    - My final approach combines both methods. We begin by scraping to pull in raw information directly from the company websites (including headings, paragraphs, list items, etc.).
    - Attempt to use this scraped text as more context for Gemini. As a fallback if gemini fails to produce a valid output, attempt to use regex to extract the names
    - A limitation of this approach is, it struggles to for companies with founders not listed on the website (especially true for larger companies).

Note: I ultimately decided to use a hybrid appraoch bcause for more small early stage startups (Pack VCs focus) founders are more likely to be listed somehwere on the website, so scraping then prompting an LLM would be helpful.


Future Improvements:
- Integrating a structured api like wikipedia or crunchbase is more reliable than scraping and may reduce hallucination and improve response accuracy.
- More robust scraping approach. Be able to recursively crawl through links as opposed to only scraping the homepage.
- Experimentation with different LLMs. Due to time and resource constraints I decided to use the gemini API since
it was free and setup was fast. However if given more time, I would experiment with different LLMS or even use multiple to validate responses. I would also do more tuning to the prompt for more reliable responses. 
- Integrate some real time search to better ground responses and provide more infromation for newer companies.



