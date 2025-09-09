from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import json
import uuid
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

from crew_manager import CrewManager

app = FastAPI(title="RankX Product Research API", version="1.0.0")

# Store for tracking job statuses
job_store = {}
executor = ThreadPoolExecutor(max_workers=2)

# Pydantic models for API
class ProductResearchRequest(BaseModel):
    product_name: str = Field(..., description="Name of the product to research")
    websites_list: List[str] = Field(..., description="List of website URLs to search")
    country_name: str = Field(..., description="Country name for regional search")
    no_keywords: int = Field(default=10, description="Maximum number of search keywords to generate")
    language: str = Field(default="English", description="Language for search queries")
    score_th: float = Field(default=0.10, description="Score threshold for filtering results")
    top_recommendations_no: int = Field(default=10, description="Number of top product recommendations")

class JobStatus(BaseModel):
    job_id: str
    status: str  # "pending", "running", "completed", "failed"
    progress: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str

# Initialize CrewManager
crew_manager = CrewManager()

def run_crew_task(job_id: str, inputs: Dict[str, Any]):
    """Background task to run the crew"""
    try:
        job_store[job_id]["status"] = "running"
        job_store[job_id]["progress"] = "Initializing agents..."
        
        # Execute the crew
        results = crew_manager.execute_crew(inputs)
        
        if results["success"]:
            job_store[job_id]["status"] = "completed"
            job_store[job_id]["results"] = results
            job_store[job_id]["completed_at"] = datetime.now()
            job_store[job_id]["progress"] = "Task completed successfully!"
        else:
            job_store[job_id]["status"] = "failed"
            job_store[job_id]["error"] = results.get("error", "Unknown error")
            job_store[job_id]["completed_at"] = datetime.now()
            
    except Exception as e:
        job_store[job_id]["status"] = "failed"
        job_store[job_id]["error"] = str(e)
        job_store[job_id]["completed_at"] = datetime.now()

@app.get("/", response_class=HTMLResponse)
async def get_home():
    """Serve the main HTML interface"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>RankX Product Research</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            .job-status { margin-top: 20px; }
            .progress-container { margin-top: 15px; }
        </style>
    </head>
    <body>
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <h1 class="text-center mb-4">RankX Product Research</h1>
                    <div class="card">
                        <div class="card-body">
                            <form id="researchForm">
                                <div class="mb-3">
                                    <label for="product_name" class="form-label">Product Name</label>
                                    <input type="text" class="form-control" id="product_name" name="product_name" 
                                           placeholder="e.g., Office air conditioners" required>
                                </div>
                                
                                <div class="mb-3">
                                    <label for="websites_list" class="form-label">Websites (one per line)</label>
                                    <textarea class="form-control" id="websites_list" name="websites_list" rows="3" 
                                              placeholder="www.amazon.com
www.electroplanet.ma
www.ikea.com" required></textarea>
                                </div>
                                
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="country_name" class="form-label">Country</label>
                                            <input type="text" class="form-control" id="country_name" name="country_name" 
                                                   value="Morocco" required>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label for="language" class="form-label">Language</label>
                                            <input type="text" class="form-control" id="language" name="language" 
                                                   value="English" required>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="row">
                                    <div class="col-md-4">
                                        <div class="mb-3">
                                            <label for="no_keywords" class="form-label">Max Keywords</label>
                                            <input type="number" class="form-control" id="no_keywords" name="no_keywords" 
                                                   value="10" min="1" max="50">
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="mb-3">
                                            <label for="score_th" class="form-label">Score Threshold</label>
                                            <input type="number" class="form-control" id="score_th" name="score_th" 
                                                   value="0.10" step="0.01" min="0" max="1">
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="mb-3">
                                            <label for="top_recommendations_no" class="form-label">Top Recommendations</label>
                                            <input type="number" class="form-control" id="top_recommendations_no" 
                                                   name="top_recommendations_no" value="10" min="1" max="50">
                                        </div>
                                    </div>
                                </div>
                                
                                <button type="submit" class="btn btn-primary w-100">Start Research</button>
                            </form>
                        </div>
                    </div>
                    
                    <div id="jobStatus" class="job-status" style="display: none;">
                        <div class="card">
                            <div class="card-body">
                                <h5>Job Status: <span id="status"></span></h5>
                                <p id="progress"></p>
                                <div class="progress-container">
                                    <div class="progress">
                                        <div id="progressBar" class="progress-bar progress-bar-striped progress-bar-animated" 
                                             role="progressbar" style="width: 0%"></div>
                                    </div>
                                </div>
                                <div id="results" style="display: none;">
                                    <hr>
                                    <h6>Results:</h6>
                                    <div id="downloadLinks"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            let currentJobId = null;
            let statusCheckInterval = null;

            document.getElementById('researchForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData(e.target);
                const data = {
                    product_name: formData.get('product_name'),
                    websites_list: formData.get('websites_list').split('\\n').map(s => s.trim()).filter(s => s),
                    country_name: formData.get('country_name'),
                    language: formData.get('language'),
                    no_keywords: parseInt(formData.get('no_keywords')),
                    score_th: parseFloat(formData.get('score_th')),
                    top_recommendations_no: parseInt(formData.get('top_recommendations_no'))
                };

                try {
                    const response = await fetch('/api/research', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(data)
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        currentJobId = result.job_id;
                        document.getElementById('jobStatus').style.display = 'block';
                        startStatusCheck();
                    } else {
                        alert('Error: ' + result.detail);
                    }
                } catch (error) {
                    alert('Error: ' + error.message);
                }
            });

            async function checkJobStatus() {
                if (!currentJobId) return;
                
                try {
                    const response = await fetch(`/api/job/${currentJobId}/status`);
                    const job = await response.json();
                    
                    document.getElementById('status').textContent = job.status;
                    document.getElementById('progress').textContent = job.progress;
                    
                    const progressBar = document.getElementById('progressBar');
                    if (job.status === 'pending') {
                        progressBar.style.width = '10%';
                    } else if (job.status === 'running') {
                        progressBar.style.width = '50%';
                    } else if (job.status === 'completed') {
                        progressBar.style.width = '100%';
                        progressBar.classList.remove('progress-bar-animated');
                        clearInterval(statusCheckInterval);
                        
                        // Show download links
                        document.getElementById('results').style.display = 'block';
                        document.getElementById('downloadLinks').innerHTML = `
                            <a href="/api/job/${currentJobId}/download/step_4_procurement_report.html" 
                               class="btn btn-success me-2" target="_blank">View Report</a>
                            <a href="/api/job/${currentJobId}/files" 
                               class="btn btn-info">View All Files</a>
                        `;
                    } else if (job.status === 'failed') {
                        progressBar.style.width = '100%';
                        progressBar.classList.remove('progress-bar-animated');
                        progressBar.classList.add('bg-danger');
                        clearInterval(statusCheckInterval);
                        alert('Job failed: ' + (job.error || 'Unknown error'));
                    }
                } catch (error) {
                    console.error('Status check failed:', error);
                }
            }

            function startStatusCheck() {
                statusCheckInterval = setInterval(checkJobStatus, 2000);
                checkJobStatus();
            }
        </script>
    </body>
    </html>
    """

@app.post("/api/research", response_model=JobResponse)
async def start_research(request: ProductResearchRequest, background_tasks: BackgroundTasks):
    """Start a new product research job"""
    
    # Validate inputs
    validation = crew_manager.validate_inputs(request.dict())
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail=validation["errors"])
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Initialize job status
    job_store[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "progress": "Job queued for processing...",
        "created_at": datetime.now(),
        "completed_at": None,
        "results": None,
        "error": None
    }