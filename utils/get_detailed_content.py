#!/usr/bin/env python3
"""
Get detailed content from database to create relevant test cases
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.retriever import LegalDocumentRetriever

def main():
    print("=" * 80)
    print("GETTING DETAILED CONTENT FOR TEST CASE CREATION")
    print("=" * 80)
    
    retriever = LegalDocumentRetriever()
    retriever.load_vector_store()
    
    # Get detailed results for different topics
    topics = [
        "constitutional rights",
        "criminal law",
        "anticipatory bail",
        "fundamental rights",
        "right to life",
        "freedom of speech",
        "contract dispute",
        "civil procedure"
    ]
    
    all_cases = []
    
    for topic in topics:
        print(f"\n--- {topic.upper()} ---")
        results = retriever.retrieve(topic, k=3)
        
        for i, result in enumerate(results):
            print(f"\nCase {i+1}:")
            print(f"Citation: {result.metadata.get('citation', 'N/A')}")
            print(f"Judges: {result.metadata.get('judges', 'N/A')}")
            print(f"Page: {result.metadata.get('page_number', 'N/A')}")
            
            # Get more content
            content = result.page_content
            print(f"Content: {content[:300]}...")
            
            # Store for analysis
            case_info = {
                'topic': topic,
                'citation': result.metadata.get('citation', ''),
                'judges': result.metadata.get('judges', []),
                'content': content[:500],
                'page': result.metadata.get('page_number', '')
            }
            all_cases.append(case_info)
    
    # Create summary
    print("\n" + "=" * 80)
    print("SUMMARY FOR TEST CASE CREATION")
    print("=" * 80)
    
    # Group by type
    constitutional_cases = [c for c in all_cases if any(term in c['content'].lower() for term in ['constitution', 'fundamental', 'right', 'article'])]
    criminal_cases = [c for c in all_cases if any(term in c['content'].lower() for term in ['criminal', 'bail', 'conviction', 'trial'])]
    civil_cases = [c for c in all_cases if any(term in c['content'].lower() for term in ['contract', 'civil', 'dispute', 'procedure'])]
    
    print(f"\nConstitutional cases found: {len(constitutional_cases)}")
    print(f"Criminal cases found: {len(criminal_cases)}")
    print(f"Civil cases found: {len(civil_cases)}")
    
    # Show sample citations
    print(f"\nSample Citations:")
    citations = list(set([c['citation'] for c in all_cases if c['citation']]))
    for citation in citations[:5]:
        print(f"  • {citation}")
    
    # Show sample judges
    print(f"\nSample Judges:")
    judges = []
    for case in all_cases:
        judges.extend(case['judges'])
    unique_judges = list(set(judges))
    for judge in unique_judges[:5]:
        print(f"  • {judge}")

if __name__ == "__main__":
    main()
