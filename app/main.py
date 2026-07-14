import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.agents.orchestrator import run_research_pipeline
from app.utils.report_export import export_to_pdf, export_to_docx

app = FastAPI(
    title="Company Research Agent",
    description=(
        "Multi-agent (AutoGen) system that researches any company via live "
        "web search and produces a downloadable PDF/DOCX report with "
        "actionable suggestions."
    ),
    version="1.0.0",
)

# In-memory job store. Swap for Redis/DB if you need persistence across restarts.
JOBS: dict[str, dict] = {}


class ResearchRequest(BaseModel):
    company_name: str = Field(..., min_length=2, examples=["Stripe"])


class ResearchResponse(BaseModel):
    job_id: str
    company_name: str
    final_report: str
    pdf_url: str
    docx_url: str


@app.get("/")
def root():
    return {
        "message": "Company Research Agent API",
        "endpoints": {
            "POST /research": "Run the full research pipeline for a company",
            "GET /download/{job_id}/pdf": "Download the PDF report",
            "GET /download/{job_id}/docx": "Download the DOCX report",
            "GET /jobs/{job_id}": "Fetch a previously generated report",
        },
    }


@app.post("/research", response_model=ResearchResponse)
def research_company(payload: ResearchRequest):
    company_name = payload.company_name.strip()
    if not company_name:
        raise HTTPException(status_code=400, detail="company_name cannot be empty")

    try:
        result = run_research_pipeline(company_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {e}")

    if not result.get("final_report"):
        raise HTTPException(status_code=500, detail="Pipeline produced an empty report")

    pdf_path = export_to_pdf(result["final_report"], company_name)
    docx_path = export_to_docx(result["final_report"], company_name)

    job_id = str(uuid.uuid4())
    JOBS[job_id] = {
        "company_name": company_name,
        "final_report": result["final_report"],
        "pdf_path": pdf_path,
        "docx_path": docx_path,
    }

    return ResearchResponse(
        job_id=job_id,
        company_name=company_name,
        final_report=result["final_report"],
        pdf_url=f"/download/{job_id}/pdf",
        docx_url=f"/download/{job_id}/docx",
    )


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/download/{job_id}/pdf")
def download_pdf(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if not os.path.exists(job["pdf_path"]):
        raise HTTPException(status_code=404, detail="PDF file not found on disk")
    filename = os.path.basename(job["pdf_path"])
    return FileResponse(job["pdf_path"], media_type="application/pdf", filename=filename)


@app.get("/download/{job_id}/docx")
def download_docx(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if not os.path.exists(job["docx_path"]):
        raise HTTPException(status_code=404, detail="DOCX file not found on disk")
    filename = os.path.basename(job["docx_path"])
    return FileResponse(
        job["docx_path"],
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=filename,
    )
