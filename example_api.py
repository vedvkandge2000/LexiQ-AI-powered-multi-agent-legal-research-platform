#!/usr/bin/env python3
"""
Example API implementation for LexiQ.
Shows how to integrate the query system into a web API.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from orchestrator import query_once
from utils.query_handler import QueryHandler
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Initialize query handler once at startup (for better performance)
query_handler = None


def init_query_handler():
    """Initialize the query handler at app startup."""
    global query_handler
    if query_handler is None:
        query_handler = QueryHandler(
            vector_store_dir="data/vector_store",
            k=5
        )
        query_handler.initialize()
        print("✓ Query handler initialized")


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "LexiQ API"
    })


@app.route('/api/query', methods=['POST'])
def handle_query():
    """
    Handle legal query requests.
    
    Request body:
    {
        "question": "What are key cases on freedom of speech?",
        "max_results": 5  # optional
    }
    
    Response:
    {
        "query": "...",
        "answer": "...",  # Markdown formatted response
        "sources": [...],  # List of case metadata
        "num_sources": 5
    }
    """
    try:
        # Get query from request
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({
                "error": "Missing 'question' in request body"
            }), 400
        
        user_question = data['question'].strip()
        
        if not user_question:
            return jsonify({
                "error": "Question cannot be empty"
            }), 400
        
        # Process query
        result = query_handler.query(user_question)
        
        # Format response
        response = {
            "query": result["query"],
            "answer": result["response"],
            "sources": result["retrieved_documents"],
            "num_sources": result["num_documents"]
        }
        
        return jsonify(response)
    
    except Exception as e:
        print(f"Error processing query: {e}")
        return jsonify({
            "error": f"Failed to process query: {str(e)}"
        }), 500


@app.route('/api/batch-query', methods=['POST'])
def handle_batch_query():
    """
    Handle multiple queries in batch.
    
    Request body:
    {
        "questions": [
            "What is Article 14?",
            "Cases on freedom of religion"
        ]
    }
    
    Response:
    {
        "results": [
            {
                "query": "...",
                "answer": "...",
                "sources": [...],
                "num_sources": 5
            },
            ...
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'questions' not in data:
            return jsonify({
                "error": "Missing 'questions' array in request body"
            }), 400
        
        questions = data['questions']
        
        if not isinstance(questions, list) or len(questions) == 0:
            return jsonify({
                "error": "Questions must be a non-empty array"
            }), 400
        
        # Process batch
        results = query_handler.batch_query(questions)
        
        # Format response
        formatted_results = []
        for result in results:
            formatted_results.append({
                "query": result["query"],
                "answer": result["response"],
                "sources": result["retrieved_documents"],
                "num_sources": result["num_documents"]
            })
        
        return jsonify({
            "results": formatted_results
        })
    
    except Exception as e:
        print(f"Error processing batch query: {e}")
        return jsonify({
            "error": f"Failed to process batch query: {str(e)}"
        }), 500


@app.route('/api/search', methods=['POST'])
def handle_search():
    """
    Pure search endpoint (no Claude, just retrieval).
    Useful for showing suggestions or exploring cases.
    
    Request body:
    {
        "query": "freedom of speech",
        "k": 10  # optional, default 5
    }
    
    Response:
    {
        "query": "...",
        "results": [
            {
                "case_title": "...",
                "citation": "...",
                "page_number": 5,
                "s3_url": "...",
                "content_preview": "..."
            },
            ...
        ],
        "num_results": 10
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                "error": "Missing 'query' in request body"
            }), 400
        
        search_query = data['query'].strip()
        k = data.get('k', 5)
        
        if not search_query:
            return jsonify({
                "error": "Query cannot be empty"
            }), 400
        
        # Perform search only (no Claude)
        retrieved_docs = query_handler.retriever.retrieve(search_query, k=k)
        metadata = query_handler.retriever.get_metadata_summary(retrieved_docs)
        
        return jsonify({
            "query": search_query,
            "results": metadata,
            "num_results": len(metadata)
        })
    
    except Exception as e:
        print(f"Error performing search: {e}")
        return jsonify({
            "error": f"Failed to perform search: {str(e)}"
        }), 500


if __name__ == '__main__':
    # Initialize query handler
    init_query_handler()
    
    # Run Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

