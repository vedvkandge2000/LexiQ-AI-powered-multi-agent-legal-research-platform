#!/usr/bin/env python3
"""
REST API for LexiQ Case Similarity Analysis.
Allows lawyers to upload cases and find similar precedents.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import tempfile
from utils.case_similarity import CaseSimilarityAnalyzer

app = Flask(__name__)
CORS(app)

# Configuration
ALLOWED_EXTENSIONS = {'pdf'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Initialize analyzer once at startup
analyzer = None


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def init_analyzer():
    """Initialize the case similarity analyzer."""
    global analyzer
    if analyzer is None:
        analyzer = CaseSimilarityAnalyzer(vector_store_dir="data/vector_store")
        analyzer.initialize()
        print("✓ Case Similarity Analyzer initialized")


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "LexiQ Case Similarity API"
    })


@app.route('/api/analyze-case-text', methods=['POST'])
def analyze_case_from_text():
    """
    Analyze a case from text description.
    
    Request body:
    {
        "case_description": "Description of the current case...",
        "k": 5  # optional, number of similar cases to retrieve
    }
    
    Response:
    {
        "current_case": "...",
        "analysis": "Full markdown analysis...",
        "similar_cases": [...],
        "num_similar_cases": 5
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'case_description' not in data:
            return jsonify({
                "error": "Missing 'case_description' in request body"
            }), 400
        
        case_description = data['case_description'].strip()
        k = data.get('k', 5)
        
        if not case_description:
            return jsonify({
                "error": "Case description cannot be empty"
            }), 400
        
        # Analyze the case
        result = analyzer.analyze_case_from_text(
            case_description=case_description,
            k=k
        )
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Error analyzing case: {e}")
        return jsonify({
            "error": f"Failed to analyze case: {str(e)}"
        }), 500


@app.route('/api/analyze-case-pdf', methods=['POST'])
def analyze_case_from_pdf():
    """
    Analyze a case from uploaded PDF.
    
    Form data:
    - file: PDF file
    - k: (optional) number of similar cases
    
    Response:
    {
        "current_case": "...",
        "analysis": "Full markdown analysis...",
        "similar_cases": [...],
        "num_similar_cases": 5,
        "pdf_metadata": {...}
    }
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                "error": "No file provided"
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                "error": "No file selected"
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                "error": "Only PDF files are allowed"
            }), 400
        
        # Get optional parameters
        k = int(request.form.get('k', 5))
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            file.save(tmp_file.name)
            tmp_path = tmp_file.name
        
        try:
            # Analyze the PDF
            result = analyzer.analyze_case_from_pdf(
                pdf_path=tmp_path,
                k=k
            )
            
            # Remove temporary file
            os.unlink(tmp_path)
            
            # Remove the local path from response
            if 'pdf_path' in result:
                result['pdf_path'] = filename
            
            return jsonify(result)
        
        except Exception as e:
            # Clean up temp file on error
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise e
    
    except Exception as e:
        print(f"Error analyzing PDF: {e}")
        return jsonify({
            "error": f"Failed to analyze PDF: {str(e)}"
        }), 500


@app.route('/api/find-similar-cases', methods=['POST'])
def find_similar_cases():
    """
    Quick search for similar cases without full Claude analysis.
    
    Request body:
    {
        "case_text": "Search text...",
        "k": 10,  # optional - number of results
        "with_scores": true,  # optional - include similarity scores
        "deduplicate": true  # optional - if true, returns k unique cases; if false, returns k chunks
    }
    
    Response:
    {
        "similar_cases": [
            {
                "case_title": "...",
                "citation": "...",
                "case_number": "...",
                "section": "...",
                "page_number": 15,
                "s3_url": "...",
                "similarity_score": 0.85,
                "content_preview": "..."
            },
            ...
        ],
        "num_results": 10,
        "deduplicated": true
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'case_text' not in data:
            return jsonify({
                "error": "Missing 'case_text' in request body"
            }), 400
        
        case_text = data['case_text'].strip()
        k = data.get('k', 10)
        with_scores = data.get('with_scores', True)
        deduplicate = data.get('deduplicate', True)  # Default to deduplication
        
        if not case_text:
            return jsonify({
                "error": "Case text cannot be empty"
            }), 400
        
        # Find similar cases
        similar_cases = analyzer.find_similar_cases_only(
            case_text=case_text,
            k=k,
            with_scores=with_scores,
            deduplicate=deduplicate
        )
        
        return jsonify({
            "similar_cases": similar_cases,
            "num_results": len(similar_cases),
            "deduplicated": deduplicate
        })
    
    except Exception as e:
        print(f"Error finding similar cases: {e}")
        return jsonify({
            "error": f"Failed to find similar cases: {str(e)}"
        }), 500


@app.route('/api/find-similar-cases-with-chunks', methods=['POST'])
def find_similar_cases_with_chunks():
    """
    Find similar cases with multiple relevant chunks per case.
    
    Request body:
    {
        "case_text": "Search text...",
        "k_cases": 5,  # optional - number of unique cases
        "max_chunks_per_case": 3  # optional - chunks per case
    }
    
    Response:
    {
        "similar_cases": [
            {
                "case_title": "...",
                "citation": "...",
                "case_number": "...",
                "s3_url": "...",
                "best_score": 0.85,
                "chunks": [
                    {
                        "section": "...",
                        "page_number": 15,
                        "chunk_id": 5,
                        "similarity_score": 0.85,
                        "content_preview": "..."
                    },
                    ...
                ]
            },
            ...
        ],
        "num_cases": 5,
        "total_chunks": 12
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'case_text' not in data:
            return jsonify({
                "error": "Missing 'case_text' in request body"
            }), 400
        
        case_text = data['case_text'].strip()
        k_cases = data.get('k_cases', 5)
        max_chunks_per_case = data.get('max_chunks_per_case', 3)
        
        if not case_text:
            return jsonify({
                "error": "Case text cannot be empty"
            }), 400
        
        # Find cases with multiple chunks
        similar_cases = analyzer.find_similar_cases_with_chunks(
            case_text=case_text,
            k_cases=k_cases,
            max_chunks_per_case=max_chunks_per_case
        )
        
        total_chunks = sum(len(case["chunks"]) for case in similar_cases)
        
        return jsonify({
            "similar_cases": similar_cases,
            "num_cases": len(similar_cases),
            "total_chunks": total_chunks
        })
    
    except Exception as e:
        print(f"Error finding similar cases with chunks: {e}")
        return jsonify({
            "error": f"Failed to find similar cases: {str(e)}"
        }), 500


@app.route('/api/compare-cases', methods=['POST'])
def compare_cases():
    """
    Compare two cases.
    
    Request body:
    {
        "case1_text": "First case description...",
        "case2_text": "Second case description..."
    }
    
    Response:
    {
        "case1": "...",
        "case2": "...",
        "comparison": "Markdown comparison analysis..."
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'case1_text' not in data or 'case2_text' not in data:
            return jsonify({
                "error": "Missing 'case1_text' or 'case2_text' in request body"
            }), 400
        
        case1_text = data['case1_text'].strip()
        case2_text = data['case2_text'].strip()
        
        if not case1_text or not case2_text:
            return jsonify({
                "error": "Both case texts must be non-empty"
            }), 400
        
        # Compare cases
        result = analyzer.compare_cases(case1_text, case2_text)
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Error comparing cases: {e}")
        return jsonify({
            "error": f"Failed to compare cases: {str(e)}"
        }), 500


if __name__ == '__main__':
    # Initialize analyzer
    init_analyzer()
    
    # Run Flask app
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)

