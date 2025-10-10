#!/usr/bin/env python3
"""
Multi-Agent Orchestrator
Runs all LexiQ agents on the same case input and aggregates results.
"""

import sys
from typing import Dict, Any
from utils.case_similarity import CaseSimilarityAnalyzer
from agents.news_relevance_agent import NewsRelevanceAgent
from agents.statute_reference_agent import StatuteReferenceAgent
from agents.bench_bias_agent import BenchBiasAgent


class MultiAgentOrchestrator:
    """Orchestrates multiple AI agents for comprehensive legal analysis."""
    
    def __init__(self, 
                 vector_store_dir: str = "data/vector_store",
                 enable_news: bool = True,
                 enable_statutes: bool = True,
                 enable_bench: bool = True):
        """
        Initialize the orchestrator with all agents.
        
        Args:
            vector_store_dir: Path to vector store
            enable_news: Enable news relevance agent
            enable_statutes: Enable statute reference agent
            enable_bench: Enable bench bias agent
        """
        # Main precedent agent (always enabled)
        self.case_analyzer = CaseSimilarityAnalyzer(vector_store_dir=vector_store_dir)
        
        # Optional agents
        self.enable_news = enable_news
        self.enable_statutes = enable_statutes
        self.enable_bench = enable_bench
        
        if enable_news:
            self.news_agent = NewsRelevanceAgent(max_results=5, period='7d')
        
        if enable_statutes:
            self.statute_agent = StatuteReferenceAgent()
        
        if enable_bench:
            self.bench_agent = BenchBiasAgent()
        
        self.is_initialized = False
    
    def initialize(self):
        """Initialize the case analyzer and vector store."""
        print("🔧 Initializing Multi-Agent System...")
        self.case_analyzer.initialize()
        self.is_initialized = True
        print("✓ All agents ready!\n")
    
    def analyze_case_complete(self, 
                              case_text: str,
                              k_precedents: int = 5,
                              max_tokens: int = 2000) -> Dict[str, Any]:
        """
        Run all enabled agents on the same case text.
        
        Args:
            case_text: The case description
            k_precedents: Number of precedents to retrieve
            max_tokens: Max tokens for AI responses
            
        Returns:
            Dictionary with results from all agents
        """
        if not self.is_initialized:
            raise ValueError("Orchestrator not initialized. Call initialize() first.")
        
        results = {}
        
        # 1. Main Precedent Analysis (Always run)
        print("\n" + "=" * 70)
        print("🏛️  AGENT 1: PRECEDENT ANALYSIS")
        print("=" * 70)
        
        try:
            precedent_result = self.case_analyzer.analyze_case_from_text(
                case_text, 
                k=k_precedents, 
                max_tokens=max_tokens
            )
            results['precedents'] = precedent_result
            print(f"✓ Found {precedent_result['num_similar_cases']} similar precedents")
        except Exception as e:
            print(f"❌ Error in precedent analysis: {e}")
            results['precedents'] = {'error': str(e)}
        
        # 2. Statute Reference Analysis (Optional)
        if self.enable_statutes:
            print("\n" + "=" * 70)
            print("⚖️  AGENT 2: STATUTE REFERENCE")
            print("=" * 70)
            
            try:
                statute_result = self.statute_agent.analyze_statutes(
                    case_text, 
                    max_tokens=max_tokens//2
                )
                results['statutes'] = statute_result
                print(f"✓ Extracted {statute_result['num_provisions']} legal provisions")
            except Exception as e:
                print(f"❌ Error in statute analysis: {e}")
                results['statutes'] = {'error': str(e)}
        
        # 3. News Relevance Analysis (Optional)
        if self.enable_news:
            print("\n" + "=" * 70)
            print("📰 AGENT 3: NEWS RELEVANCE")
            print("=" * 70)
            
            try:
                news_result = self.news_agent.find_relevant_news(
                    case_text, 
                    max_tokens=max_tokens//2
                )
                results['news'] = news_result
                print(f"✓ Found {news_result['num_articles']} relevant news articles")
            except Exception as e:
                print(f"❌ Error in news analysis: {e}")
                results['news'] = {'error': str(e)}
        
        # 4. Bench Bias Analysis (Optional - depends on precedents)
        if self.enable_bench and 'precedents' in results and 'similar_cases' in results['precedents']:
            print("\n" + "=" * 70)
            print("👨‍⚖️  AGENT 4: BENCH BIAS ANALYSIS")
            print("=" * 70)
            
            try:
                bench_result = self.bench_agent.analyze_bench_from_cases(
                    results['precedents']['similar_cases'],
                    max_tokens=max_tokens//2
                )
                results['bench'] = bench_result
                print(f"✓ Analyzed {bench_result['num_judges']} judges")
            except Exception as e:
                print(f"❌ Error in bench analysis: {e}")
                results['bench'] = {'error': str(e)}
        
        print("\n" + "=" * 70)
        print("✅ MULTI-AGENT ANALYSIS COMPLETE")
        print("=" * 70)
        
        return results
    
    def get_enabled_agents(self) -> list:
        """Get list of enabled agent names."""
        agents = ['Precedent Analysis (Main)']
        if self.enable_statutes:
            agents.append('Statute Reference')
        if self.enable_news:
            agents.append('News Relevance')
        if self.enable_bench:
            agents.append('Bench Bias')
        return agents


def main():
    """CLI interface for multi-agent orchestrator."""
    
    print("=" * 70)
    print("🤖 LexiQ Multi-Agent Legal Analyst")
    print("=" * 70)
    print()
    
    # Configure agents
    print("Configure Agents:")
    print("1. All agents enabled (default)")
    print("2. Custom configuration")
    print()
    
    config_choice = input("Select (1-2): ").strip() or "1"
    
    if config_choice == "2":
        enable_news = input("Enable News Relevance? (y/n, default y): ").strip().lower() != 'n'
        enable_statutes = input("Enable Statute Reference? (y/n, default y): ").strip().lower() != 'n'
        enable_bench = input("Enable Bench Bias? (y/n, default y): ").strip().lower() != 'n'
    else:
        enable_news = enable_statutes = enable_bench = True
    
    # Initialize orchestrator
    orchestrator = MultiAgentOrchestrator(
        enable_news=enable_news,
        enable_statutes=enable_statutes,
        enable_bench=enable_bench
    )
    
    try:
        orchestrator.initialize()
    except Exception as e:
        print(f"❌ Error initializing: {e}")
        sys.exit(1)
    
    print(f"Enabled Agents: {', '.join(orchestrator.get_enabled_agents())}")
    print()
    
    # Get case input
    print("-" * 70)
    print("📝 Enter Case Description")
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
        print("⚠️  No case description provided.")
        return
    
    # Configuration
    print()
    try:
        k = int(input("Number of precedents (default 5): ") or "5")
    except ValueError:
        k = 5
    
    # Run analysis
    print()
    try:
        results = orchestrator.analyze_case_complete(case_text, k_precedents=k)
        
        # Display results
        display_results(results, case_text)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


def display_results(results: Dict[str, Any], case_text: str):
    """Display comprehensive results from all agents."""
    
    print("\n\n" + "=" * 70)
    print("📊 COMPREHENSIVE LEGAL ANALYSIS")
    print("=" * 70)
    print()
    
    # Precedent Analysis
    if 'precedents' in results and 'analysis' in results['precedents']:
        print("## 🏛️  PRECEDENT ANALYSIS")
        print("=" * 70)
        print(results['precedents']['analysis'])
        print("\n")
    
    # Statute Analysis
    if 'statutes' in results and 'explanation' in results['statutes']:
        print("\n## ⚖️  STATUTE REFERENCE")
        print("=" * 70)
        if results['statutes']['num_provisions'] > 0:
            print(f"\nFound {results['statutes']['num_provisions']} provisions:\n")
            for prov in results['statutes']['provisions_list']:
                print(f"  • {prov}")
            print("\n" + results['statutes']['explanation'])
        else:
            print("No legal provisions found.")
        print("\n")
    
    # News Analysis
    if 'news' in results and 'analysis' in results['news']:
        print("\n## 📰 NEWS RELEVANCE")
        print("=" * 70)
        print(results['news']['analysis'])
        print("\n")
    
    # Bench Analysis
    if 'bench' in results and 'analysis' in results['bench']:
        print("\n## 👨‍⚖️  BENCH BIAS ANALYSIS")
        print("=" * 70)
        print(results['bench']['analysis'])
        print("\n")
    
    # Save option
    print("=" * 70)
    save = input("\nSave complete analysis to file? (y/n): ").strip().lower()
    
    if save == 'y':
        filename = input("Enter filename (default: complete_analysis.md): ").strip() or "complete_analysis.md"
        try:
            with open(filename, 'w') as f:
                f.write("# LexiQ Complete Legal Analysis\n\n")
                f.write("## Case Description\n\n")
                f.write(case_text[:1000] + ("..." if len(case_text) > 1000 else ""))
                f.write("\n\n---\n\n")
                
                if 'precedents' in results and 'analysis' in results['precedents']:
                    f.write("## Precedent Analysis\n\n")
                    f.write(results['precedents']['analysis'])
                    f.write("\n\n---\n\n")
                
                if 'statutes' in results and 'explanation' in results['statutes']:
                    f.write("## Statute Reference\n\n")
                    f.write(results['statutes']['explanation'])
                    f.write("\n\n---\n\n")
                
                if 'news' in results and 'analysis' in results['news']:
                    f.write("## News Relevance\n\n")
                    f.write(results['news']['analysis'])
                    f.write("\n\n---\n\n")
                
                if 'bench' in results and 'analysis' in results['bench']:
                    f.write("## Bench Bias Analysis\n\n")
                    f.write(results['bench']['analysis'])
                    f.write("\n\n")
            
            print(f"✓ Saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving: {e}")


if __name__ == "__main__":
    main()

