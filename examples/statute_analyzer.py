#!/usr/bin/env python3
"""
Statute Reference Analyzer - CLI Interface
Extracts and explains legal provisions from case text.
"""

import sys
from agents.statute_reference_agent import StatuteReferenceAgent


def main():
    """Main CLI interface for statute analysis."""
    
    print("=" * 70)
    print("⚖️  LexiQ Statute Reference Analyzer")
    print("=" * 70)
    print()
    
    agent = StatuteReferenceAgent()
    
    while True:
        print("\n" + "=" * 70)
        print("📋 OPTIONS")
        print("=" * 70)
        print("1. Analyze statutes from case text")
        print("2. Quick extraction (no explanations)")
        print("3. Exit")
        print()
        
        choice = input("Select option (1-3): ").strip()
        
        if choice == "1":
            analyze_full()
        elif choice == "2":
            quick_extract()
        elif choice == "3":
            print("\n👋 Thank you for using LexiQ Statute Analyzer!")
            break
        else:
            print("⚠️  Invalid choice.")


def analyze_full():
    """Full analysis with explanations."""
    print("\n" + "-" * 70)
    print("📝 Enter Case Text")
    print("-" * 70)
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
        print("⚠️  No text provided.")
        return
    
    print()
    agent = StatuteReferenceAgent()
    
    try:
        result = agent.analyze_statutes(case_text, max_tokens=2500)
        display_results(result)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


def quick_extract():
    """Quick extraction without explanations."""
    print("\n" + "-" * 70)
    print("🔍 Quick Extraction")
    print("-" * 70)
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
        print("⚠️  No text provided.")
        return
    
    print()
    agent = StatuteReferenceAgent()
    
    try:
        provisions = agent.quick_extract(case_text)
        
        if not provisions:
            print("No legal provisions found.")
            return
        
        print("\n" + "=" * 70)
        print("📊 EXTRACTED PROVISIONS")
        print("=" * 70)
        print()
        
        for prov_type, refs in provisions.items():
            act_name = agent.ACT_NAMES.get(prov_type, prov_type.replace('_', ' ').title())
            print(f"**{act_name}**")
            for ref in refs:
                print(f"  • Section/Article {ref}")
            print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


def display_results(result: dict):
    """Display analysis results."""
    print("\n" + "=" * 70)
    print("📊 STATUTE ANALYSIS RESULTS")
    print("=" * 70)
    print()
    
    if result['num_provisions'] == 0:
        print("No legal provisions found in the text.")
        return
    
    print(f"Found {result['num_provisions']} legal provisions:\n")
    
    # List all provisions
    for i, prov in enumerate(result['provisions_list'], 1):
        print(f"{i}. {prov}")
    
    print("\n" + "=" * 70)
    print("📖 PLAIN-ENGLISH EXPLANATIONS")
    print("=" * 70)
    print()
    print(result['explanation'])
    print()
    
    # Save option
    save = input("\nSave results to file? (y/n): ").strip().lower()
    if save == 'y':
        filename = input("Enter filename (default: statute_analysis.md): ").strip() or "statute_analysis.md"
        try:
            with open(filename, 'w') as f:
                f.write("# Statute Analysis\n\n")
                f.write("## Extracted Provisions\n\n")
                for i, prov in enumerate(result['provisions_list'], 1):
                    f.write(f"{i}. {prov}\n")
                f.write("\n## Explanations\n\n")
                f.write(result['explanation'])
            print(f"✓ Saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving: {e}")


def analyze_text(case_text: str) -> dict:
    """API function for programmatic use."""
    agent = StatuteReferenceAgent()
    return agent.analyze_statutes(case_text)


if __name__ == "__main__":
    main()

