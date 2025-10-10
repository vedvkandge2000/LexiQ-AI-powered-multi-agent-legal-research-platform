#!/usr/bin/env python3
"""
News Relevance Agent
Finds recent news articles relevant to a legal case by extracting key entities
and topics, then using Claude to provide legal-context-aware summaries.
"""

from typing import Dict, List, Any, Optional
import re
from gnews import GNews
from aws.bedrock_client import call_claude, BedrockClient


# Entity Extraction Prompt
ENTITY_EXTRACTION_PROMPT = """You are a legal entity extraction expert.

TASK:
Extract key entities, topics, legal concepts, and search keywords from the provided case text.

The extracted information should be useful for finding relevant news articles.

RULES:
- Extract: People/Organizations, Locations, Legal Concepts, Industry/Sector, Key Issues
- Return 5-10 keywords that would be effective for news searches
- Focus on terms likely to appear in news articles (not overly technical legal jargon)
- Prioritize proper nouns and specific topics

FORMAT YOUR RESPONSE AS JSON:
{
  "entities": {
    "people_organizations": ["name1", "name2"],
    "locations": ["location1", "location2"],
    "legal_concepts": ["concept1", "concept2"],
    "industries": ["industry1", "industry2"],
    "key_issues": ["issue1", "issue2"]
  },
  "search_keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
}

CASE TEXT:
"""


# News Analysis Prompt
NEWS_ANALYSIS_PROMPT = """You are a legal news analyst.

TASK:
Analyze the provided news articles and explain their relevance to the legal case context.

CASE CONTEXT:
{case_context}

NEWS ARTICLES:
{news_articles}

RULES:
- For each article, explain WHY it is relevant to the case
- Highlight connections to legal precedents, similar cases, or relevant legal developments
- Consider implications for the case strategy or legal arguments
- Be concise but insightful
- If an article is NOT relevant, briefly explain why and skip detailed analysis

FORMAT YOUR RESPONSE IN MARKDOWN:
## News Relevance Analysis

### Article 1: [Title]
**Source:** [Publisher]  
**Published:** [Date]  
**Link:** [URL]

**Relevance:** [Explain why this matters for the case - 2-3 sentences]

**Key Points:**
- Point 1
- Point 2
- Point 3

**Legal Implications:** [How this might affect case strategy or legal arguments]

---

[Repeat for each article]

## Summary
[Overall summary of how current events relate to this case]
"""


class NewsRelevanceAgent:
    """Agent for finding and analyzing news relevant to a legal case."""
    
    def __init__(self, 
                 language: str = 'en',
                 country: str = 'US',
                 max_results: int = 5,
                 period: str = '7d'):
        """
        Initialize the News Relevance Agent.
        
        Args:
            language: Language for news articles (default: 'en')
            country: Country for news search (default: 'US')
            max_results: Maximum number of articles to retrieve (default: 5)
            period: Time period for news (7d, 14d, 30d, etc.)
        """
        self.google_news = GNews(
            language=language,
            country=country,
            period=period,
            max_results=max_results
        )
        self.max_results = max_results
        
    def extract_entities_and_keywords(self, case_text: str) -> Dict[str, Any]:
        """
        Extract entities and search keywords from case text using Claude.
        
        Args:
            case_text: The case description or summary
            
        Returns:
            Dictionary containing entities and search keywords
        """
        print("🔍 Extracting entities and keywords from case text...")
        
        prompt = ENTITY_EXTRACTION_PROMPT + case_text
        
        try:
            response = call_claude(prompt, max_tokens=1000, temperature=0.2)
            
            # Try to parse JSON response
            import json
            # Extract JSON from markdown code blocks if present
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON object in response
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                json_str = json_match.group(0) if json_match else response
            
            extracted = json.loads(json_str)
            print("✓ Successfully extracted entities and keywords")
            return extracted
            
        except Exception as e:
            print(f"⚠️  Error extracting entities: {e}")
            # Fallback: Simple keyword extraction
            words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', case_text)
            keywords = list(set(words))[:5]
            return {
                "entities": {
                    "people_organizations": [],
                    "locations": [],
                    "legal_concepts": [],
                    "industries": [],
                    "key_issues": []
                },
                "search_keywords": keywords
            }
    
    def search_news(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Search for news articles using extracted keywords.
        
        Args:
            keywords: List of search keywords
            
        Returns:
            List of news articles with metadata
        """
        all_articles = []
        seen_urls = set()
        
        print(f"📰 Searching news with {len(keywords)} keyword(s)...")
        
        for keyword in keywords[:3]:  # Limit to top 3 keywords to avoid overwhelming results
            try:
                print(f"   Searching: {keyword}")
                articles = self.google_news.get_news(keyword)
                
                for article in articles:
                    url = article.get('url', '')
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        all_articles.append({
                            'title': article.get('title', 'No title'),
                            'description': article.get('description', 'No description'),
                            'url': url,
                            'published_date': article.get('published date', 'Unknown'),
                            'publisher': article.get('publisher', {}).get('title', 'Unknown'),
                            'keyword': keyword
                        })
                        
                        if len(all_articles) >= self.max_results:
                            break
                            
            except Exception as e:
                print(f"⚠️  Error searching for '{keyword}': {e}")
                continue
            
            if len(all_articles) >= self.max_results:
                break
        
        print(f"✓ Found {len(all_articles)} relevant articles")
        return all_articles[:self.max_results]
    
    def analyze_news_relevance(self, 
                               case_text: str, 
                               articles: List[Dict[str, Any]],
                               max_tokens: int = 2000) -> str:
        """
        Use Claude to analyze news relevance to the case.
        
        Args:
            case_text: The original case description
            articles: List of news articles
            max_tokens: Maximum tokens for Claude response
            
        Returns:
            Formatted analysis string
        """
        if not articles:
            return "## No News Articles Found\n\nNo relevant news articles were found for this case."
        
        print("🤖 Analyzing news relevance with Claude...")
        
        # Format articles for prompt
        articles_text = ""
        for i, article in enumerate(articles, 1):
            articles_text += f"\n### Article {i}\n"
            articles_text += f"**Title:** {article['title']}\n"
            articles_text += f"**Publisher:** {article['publisher']}\n"
            articles_text += f"**Published:** {article['published_date']}\n"
            articles_text += f"**URL:** {article['url']}\n"
            articles_text += f"**Description:** {article['description']}\n"
            articles_text += f"**Matched Keyword:** {article['keyword']}\n"
            articles_text += "---\n"
        
        prompt = NEWS_ANALYSIS_PROMPT.format(
            case_context=case_text[:2000],  # Limit context size
            news_articles=articles_text
        )
        
        try:
            analysis = call_claude(prompt, max_tokens=max_tokens, temperature=0.3, timeout=180)
            print("✓ Analysis complete")
        except Exception as e:
            print(f"⚠️ Claude timeout for news analysis: {e}")
            analysis = self._generate_fallback_news_analysis(articles)
        
        return analysis
    
    def _generate_fallback_news_analysis(self, articles: List[Dict[str, Any]]) -> str:
        """Generate fallback analysis if Claude times out."""
        analysis = "## News Relevance Analysis\n\n"
        analysis += "### Current Events Summary\n"
        analysis += "Detailed analysis temporarily unavailable due to processing timeout.\n\n"
        
        analysis += "### Relevant News Articles Found\n"
        for i, article in enumerate(articles, 1):
            analysis += f"#### Article {i}: {article['title']}\n"
            analysis += f"- **Publisher:** {article['publisher']}\n"
            analysis += f"- **Published:** {article['published_date']}\n"
            analysis += f"- **Matched Keyword:** {article['keyword']}\n"
            analysis += f"- **URL:** {article['url']}\n"
            analysis += f"- **Description:** {article['description'][:200]}...\n\n"
        
        analysis += "### Note\n"
        analysis += "Detailed legal analysis could not be generated due to processing timeout. "
        analysis += "Please try again or check the individual article links above.\n"
        
        return analysis
    
    def find_relevant_news(self, 
                          case_text: str,
                          custom_keywords: Optional[List[str]] = None,
                          max_tokens: int = 2000) -> Dict[str, Any]:
        """
        Complete pipeline: extract entities, search news, and analyze relevance.
        
        Args:
            case_text: The case description or summary
            custom_keywords: Optional list of keywords to use instead of extraction
            max_tokens: Maximum tokens for Claude analysis
            
        Returns:
            Dictionary containing entities, articles, and analysis
        """
        # Step 1: Extract entities and keywords (or use custom ones)
        if custom_keywords:
            print(f"📝 Using {len(custom_keywords)} custom keywords")
            keywords = custom_keywords
            entities = {"custom_keywords": custom_keywords}
        else:
            extracted = self.extract_entities_and_keywords(case_text)
            entities = extracted.get('entities', {})
            keywords = extracted.get('search_keywords', [])
        
        if not keywords:
            return {
                "entities": entities,
                "articles": [],
                "analysis": "⚠️ Could not extract meaningful keywords from the case text.",
                "num_articles": 0
            }
        
        # Step 2: Search for news
        articles = self.search_news(keywords)
        
        # Step 3: Analyze relevance
        analysis = self.analyze_news_relevance(case_text, articles, max_tokens=max_tokens)
        
        return {
            "entities": entities,
            "keywords": keywords,
            "articles": articles,
            "analysis": analysis,
            "num_articles": len(articles)
        }
    
    def quick_search(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Quick news search without Claude analysis.
        
        Args:
            keywords: List of search keywords
            
        Returns:
            List of news articles
        """
        return self.search_news(keywords)

