# LexiQ Agents

This directory contains specialized AI agents for different legal research tasks.

## Available Agents

### 1. News Relevance Agent

**Purpose:** Find and analyze news articles relevant to a legal case.

**Features:**
- Automatic entity and keyword extraction from case descriptions using Claude
- News search using GNews API
- Legal-context-aware analysis and summarization
- Configurable time periods (7d, 14d, 30d)
- Multi-country support (US, UK, India, Canada, Australia)

**Usage:**

```python
from agents.news_relevance_agent import NewsRelevanceAgent

# Initialize agent
agent = NewsRelevanceAgent(
    max_results=5,      # Number of articles to retrieve
    period='7d',        # Time period: 7d, 14d, 30d
    country='US',       # Country code
    language='en'       # Language code
)

# Analyze news for a case
result = agent.find_relevant_news(case_text)

# Access results
print(f"Keywords: {result['keywords']}")
print(f"Found {result['num_articles']} articles")
print(f"Analysis: {result['analysis']}")

# Or use custom keywords
result = agent.find_relevant_news(
    case_text,
    custom_keywords=['patent law', 'AI', 'tech']
)

# Quick search without analysis
articles = agent.quick_search(['Supreme Court', 'First Amendment'])
```

**Output Format:**
```python
{
    "entities": {
        "people_organizations": [...],
        "locations": [...],
        "legal_concepts": [...],
        "industries": [...],
        "key_issues": [...]
    },
    "keywords": [...],
    "articles": [
        {
            "title": "...",
            "description": "...",
            "url": "...",
            "published_date": "...",
            "publisher": "...",
            "keyword": "..."
        }
    ],
    "analysis": "...",  # Markdown formatted analysis
    "num_articles": 5
}
```

**Command Line Interface:**
```bash
# Run the interactive interface
python news_analyzer.py

# Options:
# 1. Analyze news from case description
# 2. Quick news search with custom keywords
# 3. Configure news settings
# 4. Exit
```

**API Function:**
```python
from news_analyzer import analyze_single_case_news

result = analyze_single_case_news(case_text, max_articles=5)
```

**Demo Script:**
```bash
python examples/demo_news_agent.py
```

## Agent Architecture

Each agent follows a consistent pattern:

1. **Input Processing**: Extract relevant information from user input
2. **External API Integration**: Fetch data from external sources
3. **LLM Analysis**: Use Claude for intelligent analysis and summarization
4. **Structured Output**: Return results in a consistent format

## Adding New Agents

To add a new agent:

1. Create a new file in `agents/` directory (e.g., `my_agent.py`)
2. Implement the agent class with clear methods
3. Add to `agents/__init__.py`
4. Create a corresponding main interface script (e.g., `my_agent_interface.py`)
5. Add demo in `examples/demo_my_agent.py`
6. Update this README

## Dependencies

- `boto3` - AWS Bedrock for Claude access
- `gnews` - Google News scraping
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing (if needed)

## Configuration

Agents use environment variables from `.env`:

```bash
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
```

## Best Practices

1. **Error Handling**: Always include try-except blocks for external API calls
2. **Rate Limiting**: Be mindful of API rate limits
3. **Caching**: Consider caching results for repeated queries
4. **Logging**: Use print statements or logging for debugging
5. **Testing**: Create comprehensive demos and test cases
6. **Documentation**: Document all methods with clear docstrings

## Future Agents

Planned agents for development:

- **Legal Document Generator**: Draft legal documents based on case analysis
- **Case Timeline Builder**: Create chronological timelines from case documents
- **Jurisdiction Checker**: Determine applicable jurisdictions and laws
- **Expert Witness Finder**: Locate relevant expert witnesses
- **Settlement Predictor**: Predict likely settlement amounts based on precedents

