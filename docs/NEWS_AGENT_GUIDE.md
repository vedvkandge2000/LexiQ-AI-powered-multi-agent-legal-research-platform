# LexiQ News Relevance Agent - User Guide

## Overview

The News Relevance Agent helps lawyers and legal professionals stay informed about current events relevant to their cases. It automatically:

1. **Extracts key entities and topics** from case descriptions using AI
2. **Searches recent news** using the GNews API
3. **Analyzes relevance** with Claude to provide legal-context-aware summaries

## Quick Start

### Installation

```bash
# Install the gnews package
pip install gnews

# Or install all dependencies
pip install -r requirements.txt
```

### Basic Usage

**Command Line Interface:**
```bash
python news_analyzer.py
```

**Python API:**
```python
from agents.news_relevance_agent import NewsRelevanceAgent

# Initialize agent
agent = NewsRelevanceAgent(
    max_results=5,      # Number of articles to find
    period='7d',        # Time period: '7d', '14d', '30d'
    country='US',       # Country code
    language='en'       # Language code
)

# Analyze news for your case
case_description = """
Your case description here...
"""

result = agent.find_relevant_news(case_description)

# Access results
print(f"Found {result['num_articles']} relevant articles")
print(result['analysis'])
```

## Use Cases

### 1. Patent Litigation
Find news about technology developments, competitor lawsuits, or industry trends relevant to your patent case.

```python
case_text = """
Patent infringement case involving AI recommendation algorithms.
The plaintiff claims their patents on machine learning techniques
are violated by the defendant's personalized content delivery system.
"""

result = agent.find_relevant_news(case_text)
```

### 2. Corporate Litigation
Stay informed about regulatory changes, similar cases, or company-specific news.

```python
case_text = """
Securities fraud case against a publicly traded company.
Allegations of misleading financial statements and insider trading.
"""

result = agent.find_relevant_news(case_text, max_tokens=3000)
```

### 3. Environmental Law
Track pollution incidents, regulatory changes, and similar environmental cases.

```python
# Use custom keywords for targeted search
custom_keywords = [
    "EPA regulations",
    "water pollution",
    "environmental lawsuit"
]

result = agent.find_relevant_news(
    case_text,
    custom_keywords=custom_keywords
)
```

### 4. Constitutional Law
Monitor Supreme Court decisions, First Amendment cases, and constitutional developments.

```python
agent = NewsRelevanceAgent(period='30d')  # Look back 30 days
result = agent.find_relevant_news(case_text)
```

## Features

### Automatic Entity Extraction

The agent uses Claude to intelligently extract:
- **People & Organizations**: Companies, individuals, government entities
- **Locations**: Jurisdictions, cities, states, countries
- **Legal Concepts**: Statutes, legal theories, precedents
- **Industries**: Sectors and markets involved
- **Key Issues**: Main legal questions and topics

### Intelligent News Search

- Searches across multiple keywords automatically
- Deduplicates results
- Filters by time period and country
- Supports multiple languages

### Legal-Context Analysis

Claude analyzes each article for:
- **Relevance**: Why this article matters for your case
- **Key Points**: Main takeaways from the article
- **Legal Implications**: How this might affect case strategy
- **Connection to Precedents**: Links to relevant legal principles

## Configuration Options

### Time Periods

```python
agent = NewsRelevanceAgent(period='7d')   # Last 7 days (default)
agent = NewsRelevanceAgent(period='14d')  # Last 14 days
agent = NewsRelevanceAgent(period='30d')  # Last 30 days
```

### Countries

```python
agent = NewsRelevanceAgent(country='US')  # United States (default)
agent = NewsRelevanceAgent(country='GB')  # United Kingdom
agent = NewsRelevanceAgent(country='IN')  # India
agent = NewsRelevanceAgent(country='CA')  # Canada
agent = NewsRelevanceAgent(country='AU')  # Australia
```

### Number of Results

```python
agent = NewsRelevanceAgent(max_results=5)   # 5 articles (default)
agent = NewsRelevanceAgent(max_results=10)  # 10 articles (maximum)
```

### Analysis Detail Level

```python
# Concise analysis
result = agent.find_relevant_news(case_text, max_tokens=1500)

# Balanced analysis (default)
result = agent.find_relevant_news(case_text, max_tokens=2000)

# Comprehensive analysis
result = agent.find_relevant_news(case_text, max_tokens=3000)
```

## Output Format

### Result Dictionary Structure

```python
{
    "entities": {
        "people_organizations": ["Apple Inc.", "Epic Games"],
        "locations": ["California", "European Union"],
        "legal_concepts": ["antitrust", "market dominance"],
        "industries": ["technology", "gaming"],
        "key_issues": ["app store policies", "commission rates"]
    },
    "keywords": [
        "Apple antitrust",
        "app store lawsuit",
        "Epic Games",
        "mobile platform regulation",
        "developer fees"
    ],
    "articles": [
        {
            "title": "Apple Faces New Antitrust Investigation",
            "description": "Regulators announce probe into...",
            "url": "https://...",
            "published_date": "2 days ago",
            "publisher": "Reuters",
            "keyword": "Apple antitrust"
        }
    ],
    "analysis": "## News Relevance Analysis\n\n...",
    "num_articles": 5
}
```

### Markdown Analysis Format

The `analysis` field contains formatted markdown:

```markdown
## News Relevance Analysis

### Article 1: [Title]
**Source:** Reuters  
**Published:** 2 days ago  
**Link:** https://...

**Relevance:** This article discusses recent regulatory actions
that may impact the legal theories available in your case...

**Key Points:**
- Point 1
- Point 2
- Point 3

**Legal Implications:** The new enforcement approach suggests...

---

## Summary
Overall, these articles indicate a trend toward...
```

## Advanced Usage

### Custom Keywords

Bypass automatic extraction and use your own keywords:

```python
result = agent.find_relevant_news(
    case_text,
    custom_keywords=[
        "data privacy",
        "GDPR",
        "tech regulation"
    ]
)
```

### Quick Search (No Analysis)

Get raw articles without Claude analysis:

```python
articles = agent.quick_search(["patent law", "software"])

for article in articles:
    print(f"{article['title']} - {article['url']}")
```

### Entity Extraction Only

Extract entities without searching news:

```python
extracted = agent.extract_entities_and_keywords(case_text)
print(f"Keywords: {extracted['search_keywords']}")
```

### Batch Processing

Process multiple cases:

```python
cases = [case1_text, case2_text, case3_text]

for i, case in enumerate(cases, 1):
    print(f"\nProcessing case {i}...")
    result = agent.find_relevant_news(case)
    
    # Save to file
    with open(f"case_{i}_news.md", 'w') as f:
        f.write(result['analysis'])
```

## Command Line Interface

The interactive CLI provides a user-friendly interface:

```bash
python news_analyzer.py
```

### Option 1: Analyze from Case Description
1. Enter your case description
2. Type `END` when finished
3. Configure number of articles, time period, and detail level
4. View results and optionally save to file

### Option 2: Quick Keyword Search
1. Enter comma-separated keywords
2. Configure settings
3. View articles
4. Optionally analyze with Claude

### Option 3: Advanced Configuration
1. Enter case description
2. Choose auto-extraction or custom keywords
3. Configure all parameters (articles, period, country)
4. View comprehensive results

## Examples

### Example 1: IP Litigation

```python
from agents.news_relevance_agent import NewsRelevanceAgent

agent = NewsRelevanceAgent(max_results=5, period='14d')

case = """
Patent infringement case involving smartphone display technology.
Our client holds patents on OLED screen refresh rate optimization.
Defendant is a major electronics manufacturer.
"""

result = agent.find_relevant_news(case)

print(f"Keywords: {', '.join(result['keywords'])}")
print(f"\nFound {result['num_articles']} articles:")
for article in result['articles']:
    print(f"  • {article['title']}")

print(f"\n{result['analysis']}")
```

### Example 2: Regulatory Compliance

```python
keywords = [
    "SEC enforcement",
    "securities regulation",
    "financial disclosure"
]

result = agent.find_relevant_news(
    "Securities fraud case involving tech startup",
    custom_keywords=keywords,
    max_tokens=2500
)

# Save to file
with open("regulatory_news.md", 'w') as f:
    f.write(f"# Regulatory News Analysis\n\n")
    f.write(result['analysis'])
```

### Example 3: Multi-Jurisdiction Research

```python
countries = ['US', 'GB', 'IN']
all_results = {}

for country in countries:
    agent = NewsRelevanceAgent(country=country, max_results=3)
    result = agent.find_relevant_news(case_text)
    all_results[country] = result

# Compare news across jurisdictions
for country, result in all_results.items():
    print(f"\n{country}: {result['num_articles']} articles found")
```

## Best Practices

### 1. Provide Detailed Case Descriptions
More context helps the AI extract better keywords:

✅ **Good:**
```
Patent infringement case involving Apple's Face ID technology.
Plaintiff claims their patents on 3D facial recognition using
structured light projection are violated. Case filed in Eastern
District of Texas. Key issues include claim construction and
obviousness.
```

❌ **Too Brief:**
```
Patent case about Face ID
```

### 2. Use Appropriate Time Periods
- **7 days**: Breaking news, urgent matters
- **14 days**: Balanced view of recent developments
- **30 days**: Comprehensive context, regulatory changes

### 3. Adjust Detail Level
- **Concise (1500 tokens)**: Quick overview, multiple cases
- **Balanced (2000 tokens)**: Standard use, good detail
- **Comprehensive (3000 tokens)**: Deep analysis, complex cases

### 4. Refine with Custom Keywords
If auto-extraction isn't finding relevant news, use custom keywords:

```python
# Auto-extraction misses the mark
result1 = agent.find_relevant_news(complex_case)

# Refine with specific terms
result2 = agent.find_relevant_news(
    complex_case,
    custom_keywords=["specific legal term", "industry term"]
)
```

### 5. Save Results for Reference
```python
result = agent.find_relevant_news(case_text)

# Save markdown
with open("news_analysis.md", 'w') as f:
    f.write(result['analysis'])

# Save JSON for further processing
import json
with open("news_data.json", 'w') as f:
    json.dump(result, f, indent=2)
```

## Limitations

### API Rate Limits
- GNews has rate limits on free tier
- Consider caching results for repeated queries
- Space out requests when processing multiple cases

### News Availability
- Recent cases may not have news coverage yet
- Very specialized legal topics may have limited results
- Consider broader keywords if no results found

### Language Support
- Currently optimized for English
- Other languages supported by GNews but analysis may vary

## Troubleshooting

### No Articles Found
1. Broaden time period (`period='30d'`)
2. Use more general keywords
3. Check country setting
4. Verify internet connection

### Irrelevant Results
1. Provide more detailed case description
2. Use custom keywords for precision
3. Review extracted keywords and refine

### API Errors
```python
try:
    result = agent.find_relevant_news(case_text)
except Exception as e:
    print(f"Error: {e}")
    # Fallback to quick search
    articles = agent.quick_search(["fallback", "keywords"])
```

### AWS/Claude Issues
- Verify AWS credentials in `.env`
- Check AWS region setting
- Ensure sufficient Bedrock quotas

## Integration Examples

### With Case Analyzer

```python
from case_analyzer import analyze_single_case
from agents.news_relevance_agent import NewsRelevanceAgent

# Analyze case precedents
case_analysis = analyze_single_case(case_text)

# Find relevant news
news_agent = NewsRelevanceAgent()
news_result = news_agent.find_relevant_news(case_text)

# Combined report
print("# Legal Analysis Report\n")
print("## Case Analysis")
print(case_analysis['analysis'])
print("\n## Relevant News")
print(news_result['analysis'])
```

### With Flask API

```python
from flask import Flask, request, jsonify
from agents.news_relevance_agent import NewsRelevanceAgent

app = Flask(__name__)
agent = NewsRelevanceAgent()

@app.route('/api/news', methods=['POST'])
def get_news():
    data = request.json
    case_text = data.get('case_text')
    
    result = agent.find_relevant_news(case_text)
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5001)
```

## Support

For issues or questions:
1. Check the demo: `python examples/demo_news_agent.py`
2. Run tests: `python tests/test_news_agent.py`
3. Review examples in this guide
4. Check `agents/README.md` for architecture details

## Future Enhancements

Planned features:
- RSS feed integration
- Twitter/X sentiment analysis
- Legal blog aggregation
- Email alerts for new relevant news
- Historical news search
- Multi-language support improvements

