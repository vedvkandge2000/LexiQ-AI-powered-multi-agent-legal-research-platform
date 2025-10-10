#!/usr/bin/env python3
"""
LexiQ News Analyzer - Main Interface
Finds recent news relevant to a legal case and provides legal-context-aware analysis.
"""

import sys
import os
from agents.news_relevance_agent import NewsRelevanceAgent


def main():
    """Main interface for news relevance analysis."""
    
    print("=" * 70)
    print("📰 LexiQ News Analyzer - Find Relevant Current Events")
    print("=" * 70)
    print()
    
    # Main menu
    while True:
        print("\n" + "=" * 70)
        print("📋 OPTIONS")
        print("=" * 70)
        print("1. Analyze news from case description")
        print("2. Quick news search with custom keywords")
        print("3. Configure news settings")
        print("4. Exit")
        print()
        
        choice = input("Select option (1-4): ").strip()
        
        if choice == "1":
            analyze_from_case_description()
        elif choice == "2":
            quick_keyword_search()
        elif choice == "3":
            configure_and_search()
        elif choice == "4":
            print("\n👋 Thank you for using LexiQ News Analyzer!")
            break
        else:
            print("⚠️  Invalid choice. Please select 1-4.")


def analyze_from_case_description():
    """Analyze news relevance from case description."""
    print("\n" + "-" * 70)
    print("📝 Enter Case Description")
    print("-" * 70)
    print("Describe your case (facts, legal issues, parties, etc.)")
    print("Type 'END' on a new line when finished:")
    print()
    
    lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        lines.append(line)
    
    case_text = "\n".join(lines).strip()
    
    if not case_text:
        print("⚠️  No case description provided.")
        return
    
    # Configuration options
    print("\n" + "-" * 70)
    print("⚙️  CONFIGURATION")
    print("-" * 70)
    
    try:
        max_articles = int(input("Max articles to retrieve (default 5, max 10): ") or "5")
        max_articles = min(max_articles, 10)
    except ValueError:
        max_articles = 5
    
    print("\nTime period:")
    print("1. Past 7 days (default)")
    print("2. Past 14 days")
    print("3. Past 30 days")
    period_choice = input("Select (1-3): ").strip() or "1"
    period_map = {"1": "7d", "2": "14d", "3": "30d"}
    period = period_map.get(period_choice, "7d")
    
    print("\nAnalysis detail level:")
    print("1. Concise (max_tokens=1500)")
    print("2. Balanced (max_tokens=2000)")
    print("3. Comprehensive (max_tokens=3000)")
    detail = input("Select level (1-3, default 2): ").strip() or "2"
    max_tokens_map = {"1": 1500, "2": 2000, "3": 3000}
    max_tokens = max_tokens_map.get(detail, 2000)
    
    # Initialize agent and analyze
    print()
    agent = NewsRelevanceAgent(
        max_results=max_articles,
        period=period
    )
    
    try:
        result = agent.find_relevant_news(case_text, max_tokens=max_tokens)
        display_results(result, case_text)
    except Exception as e:
        print(f"\n❌ Error analyzing news: {e}")
        import traceback
        traceback.print_exc()


def quick_keyword_search():
    """Quick news search with custom keywords."""
    print("\n" + "-" * 70)
    print("🔍 Quick Keyword Search")
    print("-" * 70)
    
    keywords_input = input("Enter keywords (comma-separated): ").strip()
    
    if not keywords_input:
        print("⚠️  No keywords provided.")
        return
    
    keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
    
    if not keywords:
        print("⚠️  No valid keywords.")
        return
    
    # Configuration
    try:
        max_articles = int(input("Max articles (default 5, max 10): ") or "5")
        max_articles = min(max_articles, 10)
    except ValueError:
        max_articles = 5
    
    print("\nTime period:")
    print("1. Past 7 days (default)")
    print("2. Past 14 days")
    print("3. Past 30 days")
    period_choice = input("Select (1-3): ").strip() or "1"
    period_map = {"1": "7d", "2": "14d", "3": "30d"}
    period = period_map.get(period_choice, "7d")
    
    # Search
    print()
    agent = NewsRelevanceAgent(max_results=max_articles, period=period)
    
    try:
        articles = agent.quick_search(keywords)
        
        print("\n" + "=" * 70)
        print(f"📰 FOUND {len(articles)} NEWS ARTICLES")
        print("=" * 70)
        print()
        
        for i, article in enumerate(articles, 1):
            print(f"{i}. **{article['title']}**")
            print(f"   Publisher: {article['publisher']}")
            print(f"   Published: {article['published_date']}")
            print(f"   Matched Keyword: {article['keyword']}")
            print(f"   URL: {article['url']}")
            print(f"   Description: {article['description'][:150]}...")
            print()
        
        if articles:
            # Option to analyze with Claude
            analyze = input("\nAnalyze these articles with Claude? (y/n): ").strip().lower()
            if analyze == 'y':
                case_context = input("Enter brief case context for analysis: ").strip()
                if case_context:
                    print("\nAnalyzing...")
                    analysis = agent.analyze_news_relevance(case_context, articles)
                    print("\n" + "=" * 70)
                    print("📊 ANALYSIS")
                    print("=" * 70)
                    print()
                    print(analysis)
                    print()
        
    except Exception as e:
        print(f"\n❌ Error searching news: {e}")
        import traceback
        traceback.print_exc()


def configure_and_search():
    """Advanced configuration and search."""
    print("\n" + "-" * 70)
    print("⚙️  Advanced Configuration")
    print("-" * 70)
    
    # Get case description
    print("\nEnter case description (Type 'END' on a new line when finished):")
    lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        lines.append(line)
    
    case_text = "\n".join(lines).strip()
    
    if not case_text:
        print("⚠️  No case description provided.")
        return
    
    # Ask if they want to provide custom keywords or let AI extract
    print("\nKeyword source:")
    print("1. Auto-extract from case (default)")
    print("2. Provide custom keywords")
    keyword_choice = input("Select (1-2): ").strip() or "1"
    
    custom_keywords = None
    if keyword_choice == "2":
        keywords_input = input("Enter keywords (comma-separated): ").strip()
        if keywords_input:
            custom_keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
    
    # Other configuration
    try:
        max_articles = int(input("Max articles (default 5, max 10): ") or "5")
        max_articles = min(max_articles, 10)
    except ValueError:
        max_articles = 5
    
    print("\nTime period:")
    print("1. Past 7 days")
    print("2. Past 14 days")
    print("3. Past 30 days")
    period_choice = input("Select (1-3, default 1): ").strip() or "1"
    period_map = {"1": "7d", "2": "14d", "3": "30d"}
    period = period_map.get(period_choice, "7d")
    
    print("\nCountry:")
    print("1. United States (default)")
    print("2. United Kingdom")
    print("3. India")
    print("4. Canada")
    print("5. Australia")
    country_choice = input("Select (1-5): ").strip() or "1"
    country_map = {"1": "US", "2": "GB", "3": "IN", "4": "CA", "5": "AU"}
    country = country_map.get(country_choice, "US")
    
    # Initialize and search
    print()
    agent = NewsRelevanceAgent(
        max_results=max_articles,
        period=period,
        country=country
    )
    
    try:
        result = agent.find_relevant_news(
            case_text,
            custom_keywords=custom_keywords,
            max_tokens=2000
        )
        display_results(result, case_text)
    except Exception as e:
        print(f"\n❌ Error analyzing news: {e}")
        import traceback
        traceback.print_exc()


def display_results(result: dict, case_text: str):
    """Display news analysis results."""
    print("\n" + "=" * 70)
    print("📊 NEWS RELEVANCE ANALYSIS RESULTS")
    print("=" * 70)
    print()
    
    # Display extracted entities
    if result.get('entities'):
        print("🔍 EXTRACTED ENTITIES")
        print("-" * 70)
        entities = result['entities']
        
        if 'people_organizations' in entities and entities['people_organizations']:
            print(f"People/Organizations: {', '.join(entities['people_organizations'])}")
        if 'locations' in entities and entities['locations']:
            print(f"Locations: {', '.join(entities['locations'])}")
        if 'legal_concepts' in entities and entities['legal_concepts']:
            print(f"Legal Concepts: {', '.join(entities['legal_concepts'])}")
        if 'industries' in entities and entities['industries']:
            print(f"Industries: {', '.join(entities['industries'])}")
        if 'key_issues' in entities and entities['key_issues']:
            print(f"Key Issues: {', '.join(entities['key_issues'])}")
        
        print()
    
    # Display search keywords
    if result.get('keywords'):
        print(f"🔑 SEARCH KEYWORDS: {', '.join(result['keywords'])}")
        print()
    
    print("=" * 70)
    print(f"📰 FOUND {result['num_articles']} RELEVANT ARTICLES")
    print("=" * 70)
    print()
    
    # Display Claude analysis
    print(result['analysis'])
    print()
    
    # Display article links for quick reference
    if result['articles']:
        print("=" * 70)
        print("📎 QUICK REFERENCE - Article Links")
        print("=" * 70)
        for i, article in enumerate(result['articles'], 1):
            print(f"{i}. {article['title']}")
            print(f"   {article['url']}")
            print()
    
    # Option to save
    print("-" * 70)
    save = input("Save results to file? (y/n): ").strip().lower()
    
    if save == 'y':
        filename = input("Enter filename (default: news_analysis.md): ").strip() or "news_analysis.md"
        try:
            with open(filename, 'w') as f:
                f.write("# LexiQ News Relevance Analysis\n\n")
                f.write("## Case Description\n\n")
                f.write(case_text[:1000] + ("..." if len(case_text) > 1000 else "") + "\n\n")
                
                if result.get('entities'):
                    f.write("## Extracted Entities\n\n")
                    entities = result['entities']
                    for key, values in entities.items():
                        if values:
                            f.write(f"**{key.replace('_', ' ').title()}:** {', '.join(values)}\n\n")
                
                if result.get('keywords'):
                    f.write(f"**Search Keywords:** {', '.join(result['keywords'])}\n\n")
                
                f.write("---\n\n")
                f.write(result['analysis'])
                f.write("\n\n## Article Links\n\n")
                
                for i, article in enumerate(result['articles'], 1):
                    f.write(f"{i}. [{article['title']}]({article['url']})\n")
                    f.write(f"   - Publisher: {article['publisher']}\n")
                    f.write(f"   - Published: {article['published_date']}\n\n")
            
            print(f"✓ Results saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving file: {e}")


def analyze_single_case_news(case_text: str, max_articles: int = 5) -> dict:
    """
    Convenience function for API/script usage.
    
    Args:
        case_text: Case description
        max_articles: Maximum articles to retrieve
        
    Returns:
        Analysis results dictionary
    """
    agent = NewsRelevanceAgent(max_results=max_articles)
    return agent.find_relevant_news(case_text)


if __name__ == "__main__":
    main()

