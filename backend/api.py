#!/usr/bin/env python3
"""
LexiQ FastAPI Backend
RESTful API for React frontend - handles all legal analysis operations
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import tempfile
import uuid
from datetime import datetime

# LexiQ imports
from utils.case_similarity import CaseSimilarityAnalyzer
from agents.news_relevance_agent import NewsRelevanceAgent
from agents.statute_reference_agent import StatuteReferenceAgent
from agents.bench_bias_agent import BenchBiasAgent
from auth.user_manager import UserManager
from chat.chat_manager import ChatManager
from security.security_enforcer import SecurityEnforcer
from security.hallucination_detector import HallucinationDetector
from utils.retriever import LegalDocumentRetriever
from aws.bedrock_client import BedrockClient

# Initialize FastAPI app
app = FastAPI(
    title="LexiQ API",
    description="AI-Powered Legal Research Platform API",
    version="2.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances (initialized lazily)
_instances = {}

def get_user_manager():
    if 'user_manager' not in _instances:
        # Use absolute path to project root's data folder
        project_root = Path(__file__).parent.parent
        users_file = project_root / "data" / "users.json"
        _instances['user_manager'] = UserManager(users_file=str(users_file))
    return _instances['user_manager']

def get_security_enforcer():
    if 'security_enforcer' not in _instances:
        _instances['security_enforcer'] = SecurityEnforcer()
    return _instances['security_enforcer']

def get_case_analyzer():
    if 'case_analyzer' not in _instances:
        project_root = Path(__file__).parent.parent
        vector_store_dir = str(project_root / "data" / "vector_store")
        analyzer = CaseSimilarityAnalyzer(vector_store_dir=vector_store_dir)
        analyzer.initialize()
        _instances['case_analyzer'] = analyzer
    return _instances['case_analyzer']

def get_news_agent():
    if 'news_agent' not in _instances:
        _instances['news_agent'] = NewsRelevanceAgent(max_results=5, period='7d')
    return _instances['news_agent']

def get_statute_agent():
    if 'statute_agent' not in _instances:
        _instances['statute_agent'] = StatuteReferenceAgent()
    return _instances['statute_agent']

def get_bench_agent():
    if 'bench_agent' not in _instances:
        _instances['bench_agent'] = BenchBiasAgent()
    return _instances['bench_agent']

def get_chat_manager():
    if 'chat_manager' not in _instances:
        project_root = Path(__file__).parent.parent
        vector_store_dir = str(project_root / "data" / "vector_store")
        bedrock = BedrockClient()
        retriever = LegalDocumentRetriever(vector_store_dir=vector_store_dir)
        retriever.load_vector_store()
        _instances['chat_manager'] = ChatManager(bedrock_client=bedrock, retriever=retriever)
    return _instances['chat_manager']

def get_hallucination_detector():
    if 'hallucination_detector' not in _instances:
        project_root = Path(__file__).parent.parent
        vector_store_dir = str(project_root / "data" / "vector_store")
        retriever = LegalDocumentRetriever(vector_store_dir=vector_store_dir)
        retriever.load_vector_store()
        _instances['hallucination_detector'] = HallucinationDetector(retriever=retriever)
    return _instances['hallucination_detector']


# =============================================================================
# Pydantic Models
# =============================================================================

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str
    full_name: Optional[str] = None
    role: str = "user"

class AuthResponse(BaseModel):
    success: bool
    message: str
    user: Optional[Dict[str, Any]] = None
    token: Optional[str] = None

class CaseAnalysisRequest(BaseModel):
    case_text: str = Field(..., min_length=10, description="Case description text")
    num_precedents: int = Field(default=5, ge=1, le=10)
    enable_statutes: bool = True
    enable_news: bool = True
    enable_bench: bool = True
    user_id: Optional[str] = None

class CaseAnalysisResponse(BaseModel):
    success: bool
    request_id: str
    security_check: Dict[str, Any]
    precedents: Optional[Dict[str, Any]] = None
    statutes: Optional[Dict[str, Any]] = None
    news: Optional[Dict[str, Any]] = None
    bench: Optional[Dict[str, Any]] = None
    hallucination_check: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class ChatStartRequest(BaseModel):
    user_id: str
    case_text: Optional[str] = None
    case_title: Optional[str] = None
    similar_cases: Optional[List[Dict]] = None

class ChatMessageRequest(BaseModel):
    session_id: str
    message: str
    use_rag: bool = True

class ChatResponse(BaseModel):
    success: bool
    session_id: Optional[str] = None
    response: Optional[str] = None
    precedent_citations: Optional[List[str]] = None
    suggested_questions: Optional[List[str]] = None
    error: Optional[str] = None


# =============================================================================
# Health & Status Endpoints
# =============================================================================

@app.get("/")
async def root():
    return {"status": "ok", "service": "LexiQ API", "version": "2.0.0"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "api": "running",
            "vector_store": "available"
        }
    }

@app.get("/api/status")
async def api_status():
    """Check initialization status of all services"""
    return {
        "initialized": {
            "case_analyzer": 'case_analyzer' in _instances,
            "news_agent": 'news_agent' in _instances,
            "statute_agent": 'statute_agent' in _instances,
            "bench_agent": 'bench_agent' in _instances,
            "chat_manager": 'chat_manager' in _instances
        }
    }


# =============================================================================
# Authentication Endpoints
# =============================================================================

@app.post("/api/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Authenticate user with username and password"""
    user_manager = get_user_manager()
    
    user = user_manager.authenticate(request.username, request.password)
    
    if user:
        # Generate a simple session token (in production, use proper JWT)
        token = str(uuid.uuid4())
        return AuthResponse(
            success=True,
            message=f"Welcome back, {user['full_name']}!",
            user=user,
            token=token
        )
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")

@app.post("/api/auth/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """Register a new user"""
    user_manager = get_user_manager()
    
    result = user_manager.register(
        username=request.username,
        password=request.password,
        email=request.email,
        full_name=request.full_name,
        role=request.role
    )
    
    if result['success']:
        return AuthResponse(
            success=True,
            message="Account created successfully! Please log in."
        )
    else:
        raise HTTPException(status_code=400, detail=result.get('error', 'Registration failed'))

@app.get("/api/auth/user/{username}")
async def get_user(username: str):
    """Get user information"""
    user_manager = get_user_manager()
    user = user_manager.get_user(username)
    
    if user:
        return {"success": True, "user": user}
    else:
        raise HTTPException(status_code=404, detail="User not found")


# =============================================================================
# Case Analysis Endpoints
# =============================================================================

@app.post("/api/analyze", response_model=CaseAnalysisResponse)
async def analyze_case(request: CaseAnalysisRequest):
    """
    Full case analysis with all agents.
    Returns precedents, statutes, news, and bench bias analysis.
    """
    request_id = str(uuid.uuid4())[:8]
    
    try:
        # Security check first
        security_enforcer = get_security_enforcer()
        security_result = security_enforcer.process_case_input(
            case_text=request.case_text,
            user_id=request.user_id or "anonymous"
        )
        
        if not security_result['success']:
            return CaseAnalysisResponse(
                success=False,
                request_id=request_id,
                security_check=security_result,
                error=f"Security check failed: {security_result.get('error', 'Unknown error')}"
            )
        
        safe_case_text = security_result['processed_text']
        
        # Initialize response
        response_data = {
            "success": True,
            "request_id": request_id,
            "security_check": {
                "pii_detected": security_result['security_metadata']['pii_detected'],
                "num_redactions": security_result['security_metadata']['num_redactions'],
                "risk_score": security_result['security_metadata']['risk_score']
            }
        }
        
        # 1. Precedent Analysis (always run)
        case_analyzer = get_case_analyzer()
        precedent_result = case_analyzer.analyze_case_from_text(
            safe_case_text, 
            k=request.num_precedents, 
            max_tokens=2000
        )
        response_data['precedents'] = {
            "analysis": precedent_result['analysis'],
            "similar_cases": precedent_result['similar_cases'],
            "num_similar_cases": precedent_result['num_similar_cases']
        }
        
        # Hallucination check
        hallucination_detector = get_hallucination_detector()
        hallucination_check = hallucination_detector.detect_hallucinations(
            input_query=request.case_text,
            output_text=precedent_result['analysis'],
            user_id=request.user_id or "anonymous"
        )
        response_data['hallucination_check'] = hallucination_check
        
        # 2. Statute Analysis
        if request.enable_statutes:
            statute_agent = get_statute_agent()
            statute_result = statute_agent.analyze_statutes(safe_case_text, max_tokens=1500)
            response_data['statutes'] = statute_result
        
        # 3. News Analysis
        if request.enable_news:
            news_agent = get_news_agent()
            news_result = news_agent.find_relevant_news(safe_case_text, max_tokens=1500)
            response_data['news'] = news_result
        
        # 4. Bench Bias Analysis
        if request.enable_bench and 'similar_cases' in precedent_result:
            bench_agent = get_bench_agent()
            bench_result = bench_agent.analyze_bench_from_cases(
                precedent_result['similar_cases'], 
                max_tokens=1500
            )
            response_data['bench'] = bench_result
        
        return CaseAnalysisResponse(**response_data)
        
    except Exception as e:
        return CaseAnalysisResponse(
            success=False,
            request_id=request_id,
            security_check={},
            error=str(e)
        )

@app.post("/api/analyze/precedents")
async def analyze_precedents_only(request: CaseAnalysisRequest):
    """Quick precedent analysis only"""
    try:
        security_enforcer = get_security_enforcer()
        security_result = security_enforcer.process_case_input(
            case_text=request.case_text,
            user_id=request.user_id or "anonymous"
        )
        
        if not security_result['success']:
            raise HTTPException(status_code=400, detail=security_result.get('error'))
        
        case_analyzer = get_case_analyzer()
        result = case_analyzer.analyze_case_from_text(
            security_result['processed_text'],
            k=request.num_precedents,
            max_tokens=2000
        )
        
        return {"success": True, **result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/quick-search")
async def quick_search(case_text: str = Form(...), k: int = Form(default=10)):
    """Fast similarity search without Claude analysis"""
    try:
        case_analyzer = get_case_analyzer()
        similar_cases = case_analyzer.find_similar_cases_only(
            case_text=case_text,
            k=k,
            with_scores=True,
            deduplicate=True
        )
        
        return {"success": True, "similar_cases": similar_cases, "count": len(similar_cases)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/pdf")
async def analyze_pdf(
    file: UploadFile = File(...),
    num_precedents: int = Form(default=5),
    user_id: Optional[str] = Form(default=None)
):
    """Analyze case from PDF upload"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            case_analyzer = get_case_analyzer()
            result = case_analyzer.analyze_case_from_pdf(
                pdf_path=tmp_path,
                k=num_precedents,
                max_tokens=2000
            )
            
            return {"success": True, **result}
            
        finally:
            # Clean up temp file
            os.unlink(tmp_path)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Individual Agent Endpoints
# =============================================================================

@app.post("/api/agents/statutes")
async def analyze_statutes(case_text: str = Form(...)):
    """Extract and explain legal statutes"""
    try:
        statute_agent = get_statute_agent()
        result = statute_agent.analyze_statutes(case_text, max_tokens=1500)
        return {"success": True, **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agents/news")
async def analyze_news(case_text: str = Form(...), max_articles: int = Form(default=5)):
    """Find relevant news articles"""
    try:
        news_agent = get_news_agent()
        result = news_agent.find_relevant_news(case_text, max_tokens=1500)
        return {"success": True, **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agents/bench")
async def analyze_bench(similar_cases: List[Dict] = None):
    """Analyze bench bias from cases"""
    try:
        if not similar_cases:
            raise HTTPException(status_code=400, detail="similar_cases required")
        
        bench_agent = get_bench_agent()
        result = bench_agent.analyze_bench_from_cases(similar_cases, max_tokens=1500)
        return {"success": True, **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Chat Endpoints
# =============================================================================

@app.post("/api/chat/start", response_model=ChatResponse)
async def start_chat(request: ChatStartRequest):
    """Start a new chat session"""
    try:
        chat_manager = get_chat_manager()
        result = chat_manager.start_new_chat(
            user_id=request.user_id,
            case_text=request.case_text,
            case_title=request.case_title,
            similar_cases=request.similar_cases
        )
        
        return ChatResponse(
            success=result['success'],
            session_id=result.get('session_id'),
            response=result.get('initial_analysis'),
            error=result.get('error')
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/message", response_model=ChatResponse)
async def send_chat_message(request: ChatMessageRequest):
    """Send a message in a chat session"""
    try:
        chat_manager = get_chat_manager()
        result = chat_manager.send_message(
            session_id=request.session_id,
            user_message=request.message,
            use_rag=request.use_rag
        )
        
        return ChatResponse(
            success=result['success'],
            session_id=request.session_id,
            response=result.get('response'),
            precedent_citations=result.get('precedent_citations'),
            suggested_questions=result.get('suggested_questions'),
            error=result.get('error')
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/history/{session_id}")
async def get_chat_history(session_id: str, limit: int = 50):
    """Get chat history for a session"""
    try:
        chat_manager = get_chat_manager()
        messages = chat_manager.get_chat_history(session_id, limit=limit)
        return {"success": True, "messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/sessions/{user_id}")
async def get_user_sessions(user_id: str, limit: int = 20):
    """Get all chat sessions for a user"""
    try:
        chat_manager = get_chat_manager()
        sessions = chat_manager.get_user_chats(user_id, limit=limit)
        return {"success": True, "sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/chat/{session_id}")
async def delete_chat(session_id: str):
    """Delete a chat session"""
    try:
        chat_manager = get_chat_manager()
        success = chat_manager.delete_chat(session_id)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/export/{session_id}")
async def export_chat(session_id: str, format: str = "markdown"):
    """Export chat session"""
    try:
        chat_manager = get_chat_manager()
        content = chat_manager.export_chat(session_id, format=format)
        
        if content:
            return {"success": True, "content": content, "format": format}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Report Generation
# =============================================================================

@app.post("/api/report/generate")
async def generate_report(
    case_text: str = Form(...),
    precedents: Optional[str] = Form(default=None),
    statutes: Optional[str] = Form(default=None),
    news: Optional[str] = Form(default=None),
    bench: Optional[str] = Form(default=None)
):
    """Generate downloadable markdown report"""
    report = "# LexiQ Legal Analysis Report\n\n"
    report += f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
    report += "---\n\n"
    
    report += "## Case Description\n\n"
    report += case_text[:1000] + ("..." if len(case_text) > 1000 else "")
    report += "\n\n---\n\n"
    
    if precedents:
        report += "## Precedent Analysis\n\n"
        report += precedents
        report += "\n\n---\n\n"
    
    if statutes:
        report += "## Statute Reference\n\n"
        report += statutes
        report += "\n\n---\n\n"
    
    if news:
        report += "## News Relevance\n\n"
        report += news
        report += "\n\n---\n\n"
    
    if bench:
        report += "## Bench Bias Analysis\n\n"
        report += bench
        report += "\n\n"
    
    return {
        "success": True,
        "report": report,
        "filename": f"lexiq_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.md"
    }


# =============================================================================
# Main entry point
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

