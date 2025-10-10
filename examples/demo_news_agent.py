#!/usr/bin/env python3
"""
Demo: News Relevance Agent
Shows how to use the NewsRelevanceAgent to find relevant current events.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.news_relevance_agent import NewsRelevanceAgent


def demo_basic_usage():
    """Demo 1: Basic usage with case description."""
    print("=" * 70)
    print("DEMO 1: Basic Case News Analysis")
    print("=" * 70)
    print()
    
    # Sample case description
    case_text = """
    A technology company is being sued for patent infringement related to 
    artificial intelligence algorithms used in their recommendation system.
    The plaintiff claims that the defendant's AI system violates their patents
    on machine learning techniques for personalized content delivery.
    The case involves questions about the patentability of AI algorithms and
    the scope of patent protection in the tech industry.
    """
    
    print("Case Description:")
    print(case_text)
    print()
    
    # Initialize agent
    agent = NewsRelevanceAgent(max_results=5, period='7d')
    
    # Analyze
    print("Analyzing news relevance...\n")
    result = agent.find_relevant_news(case_text, max_tokens=2000)
    
    # Display results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print()
    print(f"Keywords Used: {', '.join(result['keywords'])}")
    print(f"Articles Found: {result['num_articles']}")
    print()
    print("Analysis:")
    print(result['analysis'])
    print()


def demo_custom_keywords():
    """Demo 2: Using custom keywords instead of auto-extraction."""
    print("\n" + "=" * 70)
    print("DEMO 2: Custom Keyword Search")
    print("=" * 70)
    print()
    
    case_text = """
    A landmark environmental case involving corporate liability for pollution
    of a major river system affecting thousands of residents.
    """
    
    # Custom keywords for more targeted search
    custom_keywords = [
        "environmental lawsuit",
        "water pollution",
        "corporate liability",
        "EPA regulations"
    ]
    
    print("Case Description:")
    print(case_text)
    print()
    print(f"Using Custom Keywords: {', '.join(custom_keywords)}")
    print()
    
    # Initialize agent
    agent = NewsRelevanceAgent(max_results=5, period='14d')
    
    # Analyze with custom keywords
    result = agent.find_relevant_news(case_text, custom_keywords=custom_keywords)
    
    # Display results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print()
    print(f"Articles Found: {result['num_articles']}")
    print()
    
    if result['articles']:
        print("Articles:")
        for i, article in enumerate(result['articles'], 1):
            print(f"\n{i}. {article['title']}")
            print(f"   Publisher: {article['publisher']}")
            print(f"   Published: {article['published_date']}")
            print(f"   URL: {article['url']}")
            print(f"   Description: {article['description'][:150]}...")


def demo_quick_search():
    """Demo 3: Quick search without full analysis."""
    print("\n" + "=" * 70)
    print("DEMO 3: Quick News Search")
    print("=" * 70)
    print()
    
    keywords = ["Supreme Court", "constitutional law", "First Amendment"]
    
    print(f"Searching for: {', '.join(keywords)}")
    print()
    
    # Initialize agent
    agent = NewsRelevanceAgent(max_results=5, period='7d')
    
    # Quick search
    articles = agent.quick_search(keywords)
    
    # Display results
    print(f"Found {len(articles)} articles:\n")
    for i, article in enumerate(articles, 1):
        print(f"{i}. {article['title']}")
        print(f"   {article['publisher']} - {article['published_date']}")
        print(f"   {article['url']}")
        print()


def demo_entity_extraction():
    """Demo 4: Entity extraction only."""
    print("\n" + "=" * 70)
    print("DEMO 4: Entity Extraction")
    print("=" * 70)
    print()
    
    case_text = """
    Microsoft Corporation is facing antitrust allegations in the European Union
    regarding its bundling of Teams with Office 365. Slack Technologies has
    filed complaints with the European Commission, arguing that Microsoft's
    practices constitute anticompetitive behavior in violation of EU competition law.
    The case involves issues of market dominance, tying arrangements, and
    software licensing practices in the enterprise communication sector.
    """
    
    print("Case Description:")
    print(case_text)
    print()
    
    # Initialize agent
    agent = NewsRelevanceAgent()
    
    # Extract entities
    print("Extracting entities and keywords...\n")
    extracted = agent.extract_entities_and_keywords(case_text)
    
    # Display extracted information
    print("=" * 70)
    print("EXTRACTED INFORMATION")
    print("=" * 70)
    print()
    
    if 'entities' in extracted:
        entities = extracted['entities']
        print("Entities:")
        for category, items in entities.items():
            if items:
                print(f"  {category.replace('_', ' ').title()}: {', '.join(items)}")
    
    print()
    if 'search_keywords' in extracted:
        print(f"Search Keywords: {', '.join(extracted['search_keywords'])}")
    print()


def demo_different_time_periods():
    """Demo 5: Comparing different time periods."""
    print("\n" + "=" * 70)
    print("DEMO 5: Different Time Periods")
    print("=" * 70)
    print()
    
    keywords = ["cryptocurrency regulation", "SEC"]
    
    periods = ['7d', '14d', '30d']
    
    for period in periods:
        print(f"\n--- Last {period[:-1]} days ---")
        agent = NewsRelevanceAgent(max_results=3, period=period)
        articles = agent.quick_search(keywords)
        print(f"Found {len(articles)} articles")
        for article in articles[:2]:  # Show first 2
            print(f"  • {article['title']} ({article['published_date']})")


def main():
    """Run all demos."""
    print("\n")
    print("=" * 70)
    print("📰 LexiQ News Relevance Agent - Demo Suite")
    print("=" * 70)
    print()
    print("This demo shows various ways to use the News Relevance Agent.")
    print()
    
    demos = [
        ("Basic Case News Analysis", demo_basic_usage),
        ("Custom Keyword Search", demo_custom_keywords),
        ("Quick News Search", demo_quick_search),
        ("Entity Extraction", demo_entity_extraction),
        ("Different Time Periods", demo_different_time_periods),
    ]
    
    print("Available Demos:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"{i}. {name}")
    print("6. Run all demos")
    print()
    
    choice = input("Select demo (1-6): ").strip()
    
    try:
        if choice == '6':
            for name, demo_func in demos:
                print("\n\n")
                demo_func()
                input("\nPress Enter to continue to next demo...")
        else:
            idx = int(choice) - 1
            if 0 <= idx < len(demos):
                demos[idx][1]()
            else:
                print("Invalid choice.")
    except Exception as e:
        print(f"\n❌ Error running demo: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("Demo Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()

