#!/usr/bin/env python3
"""
LexiQ Case Analyzer - Main Interface for Lawyers
Helps lawyers find similar precedents for their current case.
"""

import sys
import os
from utils.case_similarity import CaseSimilarityAnalyzer


def main():
    """Main interface for case similarity analysis."""
    
    print("=" * 70)
    print("⚖️  LexiQ Case Analyzer - Find Similar Precedents")
    print("=" * 70)
    print()
    
    # Initialize analyzer
    analyzer = CaseSimilarityAnalyzer(vector_store_dir="data/vector_store")
    
    try:
        analyzer.initialize()
    except Exception as e:
        print(f"❌ Error initializing analyzer: {e}")
        sys.exit(1)
    
    # Main menu
    while True:
        print("\n" + "=" * 70)
        print("📋 OPTIONS")
        print("=" * 70)
        print("1. Analyze case from text description")
        print("2. Analyze case from PDF file")
        print("3. Quick search for similar cases (no analysis)")
        print("4. Exit")
        print()
        
        choice = input("Select option (1-4): ").strip()
        
        if choice == "1":
            analyze_from_text(analyzer)
        elif choice == "2":
            analyze_from_pdf(analyzer)
        elif choice == "3":
            quick_search(analyzer)
        elif choice == "4":
            print("\n👋 Thank you for using LexiQ Case Analyzer!")
            break
        else:
            print("⚠️  Invalid choice. Please select 1-4.")


def analyze_from_text(analyzer: CaseSimilarityAnalyzer):
    """Analyze case from text input."""
    print("\n" + "-" * 70)
    print("📝 Enter Case Description")
    print("-" * 70)
    print("Describe your current case (facts, legal issues, parties, etc.)")
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
    
    # Ask for number of similar cases
    print()
    try:
        k = int(input("How many similar cases to retrieve? (default 5, max 20): ") or "5")
        k = min(k, 20)  # Cap at 20 to avoid overwhelming responses
    except ValueError:
        k = 5
    
    # Ask for response detail level
    print("\nResponse Detail Level:")
    print("1. Concise (max_tokens=1000)")
    print("2. Balanced (max_tokens=2000)")
    print("3. Comprehensive (max_tokens=3000)")
    detail = input("Select level (1-3, default 2): ").strip() or "2"
    
    max_tokens_map = {"1": 1000, "2": 2000, "3": 3000}
    max_tokens = max_tokens_map.get(detail, 2000)
    
    # Analyze
    print()
    try:
        result = analyzer.analyze_case_from_text(case_text, k=k, max_tokens=max_tokens)
        display_results(result)
    except Exception as e:
        print(f"\n❌ Error analyzing case: {e}")


def analyze_from_pdf(analyzer: CaseSimilarityAnalyzer):
    """Analyze case from PDF file."""
    print("\n" + "-" * 70)
    print("📄 Analyze Case from PDF")
    print("-" * 70)
    
    pdf_path = input("Enter path to PDF file: ").strip()
    
    if not pdf_path:
        print("⚠️  No path provided.")
        return
    
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return
    
    # Ask for number of similar cases
    print()
    try:
        k = int(input("How many similar cases to retrieve? (default 5, max 20): ") or "5")
        k = min(k, 20)  # Cap at 20
    except ValueError:
        k = 5
    
    # Ask for response detail level
    print("\nResponse Detail Level:")
    print("1. Concise (max_tokens=1000)")
    print("2. Balanced (max_tokens=2000)")
    print("3. Comprehensive (max_tokens=3000)")
    detail = input("Select level (1-3, default 2): ").strip() or "2"
    
    max_tokens_map = {"1": 1000, "2": 2000, "3": 3000}
    max_tokens = max_tokens_map.get(detail, 2000)
    
    # Analyze
    print()
    try:
        result = analyzer.analyze_case_from_pdf(pdf_path, k=k, max_tokens=max_tokens)
        display_results(result)
    except Exception as e:
        print(f"\n❌ Error analyzing PDF: {e}")


def quick_search(analyzer: CaseSimilarityAnalyzer):
    """Quick search without full Claude analysis."""
    print("\n" + "-" * 70)
    print("🔍 Quick Search")
    print("-" * 70)
    
    # Step 1: Choose search mode
    print("\nSearch Mode:")
    print("1. Unique Cases (deduplicated) - One result per case")
    print("2. All Chunks - May include multiple chunks from same case")
    print("3. Grouped by Case - Multiple relevant chunks per case")
    print()
    
    mode_choice = input("Select mode (1-3, default 1): ").strip() or "1"
    
    # Step 2: Enter search text
    print("\nEnter search text (case facts, legal issues, etc.):")
    search_text = input().strip()
    
    if not search_text:
        print("⚠️  No search text provided.")
        return
    
    # Step 3: Configure parameters based on mode
    if mode_choice == "3":
        # Grouped mode
        try:
            k_cases = int(input("How many unique cases? (default 5): ") or "5")
            max_chunks = int(input("Max chunks per case? (default 3): ") or "3")
        except ValueError:
            k_cases = 5
            max_chunks = 3
        
        print()
        try:
            similar_cases = analyzer.find_similar_cases_with_chunks(
                search_text, 
                k_cases=k_cases, 
                max_chunks_per_case=max_chunks
            )
            
            print("\n" + "=" * 70)
            total_chunks = sum(len(case['chunks']) for case in similar_cases)
            print(f"🔍 SEARCH RESULTS ({len(similar_cases)} cases, {total_chunks} chunks)")
            print("=" * 70)
            print()
            
            for i, case in enumerate(similar_cases, 1):
                print(f"{i}. **{case['case_title']}**")
                print(f"   Citation: {case['citation']}")
                print(f"   Case Number: {case['case_number']}")
                print(f"   Best Similarity: {case['best_score']:.4f}")
                if case['s3_url']:
                    print(f"   📄 PDF: {case['s3_url']}")
                print(f"\n   Relevant Chunks ({len(case['chunks'])}):")
                
                for j, chunk in enumerate(case['chunks'], 1):
                    print(f"   {j}. Page {chunk['page_number']}, Section: {chunk['section'][:40]}...")
                    print(f"      Similarity: {chunk['similarity_score']:.4f}")
                    print(f"      {chunk['content_preview'][:100]}...")
                print()
        
        except Exception as e:
            print(f"\n❌ Error performing search: {e}")
    
    else:
        # Deduplicated or non-deduplicated mode
        try:
            k = int(input("How many results? (default 10): ") or "10")
        except ValueError:
            k = 10
        
        deduplicate = (mode_choice == "1")  # True for mode 1, False for mode 2
        
        print()
        try:
            similar_cases = analyzer.find_similar_cases_only(
                search_text, 
                k=k, 
                with_scores=True,
                deduplicate=deduplicate
            )
            
            print("\n" + "=" * 70)
            result_type = "unique cases" if deduplicate else "chunks"
            print(f"🔍 SEARCH RESULTS ({len(similar_cases)} {result_type} found)")
            print("=" * 70)
            print()
            
            for i, case in enumerate(similar_cases, 1):
                score = case.get('similarity_score', 0)
                print(f"{i}. **{case['case_title']}**")
                print(f"   Citation: {case['citation']}")
                print(f"   Case Number: {case['case_number']}")
                print(f"   Page Number: {case.get('page_number', 'N/A')}")
                print(f"   Similarity: {score:.4f}")
                print(f"   Section: {case.get('section', 'N/A')}")
                if case['s3_url']:
                    print(f"   📄 PDF: {case['s3_url']}")
                print(f"   Preview: {case['content_preview'][:150]}...")
                print()
        
        except Exception as e:
            print(f"\n❌ Error performing search: {e}")


def display_results(result: dict):
    """Display analysis results."""
    print("\n" + "=" * 70)
    print("📊 CASE ANALYSIS RESULTS")
    print("=" * 70)
    print()
    
    # Display the full analysis
    print(result["analysis"])
    print()
    
    print("=" * 70)
    print(f"📚 Retrieved {result['num_similar_cases']} similar precedents")
    print("=" * 70)
    print()
    
    # Display quick reference
    print("QUICK REFERENCE - Similar Cases:")
    for i, case in enumerate(result['similar_cases'], 1):
        print(f"\n{i}. {case['case_title']}")
        print(f"   {case['citation']}")
        print(f"   Case Number: {case['case_number']}")
        print(f"   Page Number: {case.get('page_number', 'N/A')}")
        if case['s3_url']:
            print(f"   📄 {case['s3_url']}")
    
    # Option to save
    print("\n" + "-" * 70)
    save = input("Save results to file? (y/n): ").strip().lower()
    
    if save == 'y':
        filename = input("Enter filename (default: case_analysis.md): ").strip() or "case_analysis.md"
        try:
            with open(filename, 'w') as f:
                f.write("# LexiQ Case Analysis\n\n")
                f.write("## Case Description\n\n")
                f.write(result['current_case'][:1000] + "...\n\n")
                f.write("## Analysis\n\n")
                f.write(result['analysis'])
                f.write("\n\n## Similar Cases Reference\n\n")
                for i, case in enumerate(result['similar_cases'], 1):
                    f.write(f"{i}. **{case['case_title']}** ({case['citation']})\n")
                    f.write(f"   - Case Number: {case['case_number']}\n")
                    f.write(f"   - Page Number: {case.get('page_number', 'N/A')}\n")
                    if case['s3_url']:
                        f.write(f"   - [View PDF]({case['s3_url']})\n")
                    f.write("\n")
            
            print(f"✓ Results saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving file: {e}")


def analyze_single_case(case_input: str, is_pdf: bool = False) -> dict:
    """
    Convenience function to analyze a single case.
    For API/script usage.
    
    Args:
        case_input: Either case description text or path to PDF
        is_pdf: True if case_input is a PDF path
        
    Returns:
        Analysis results dictionary
    """
    analyzer = CaseSimilarityAnalyzer(vector_store_dir="data/vector_store")
    analyzer.initialize()
    
    if is_pdf:
        return analyzer.analyze_case_from_pdf(case_input, k=5)
    else:
        return analyzer.analyze_case_from_text(case_input, k=5)


if __name__ == "__main__":
    main()

