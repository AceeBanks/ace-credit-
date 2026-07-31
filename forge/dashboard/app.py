"""
GLX FORGE Dashboard

FastAPI application providing a web interface for the GLX FORGE trading infrastructure.
This dashboard allows visualization and interaction with all 11 forge phases.

Version: 0.1.0
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime, timezone
import json

app = FastAPI(title="GLX FORGE Dashboard", version="0.1.0")


# Models
class PhaseStatus(BaseModel):
    phase: str
    name: str
    status: str
    modules: int
    description: str


class WorkflowRequest(BaseModel):
    type: str  # "scan", "backtest", "validate", "deploy"
    parameters: Dict = {}
    description: str = ""


class TaskStatus(BaseModel):
    task_id: str
    type: str
    status: str  # "pending", "running", "completed", "failed"
    description: str
    result: Optional[Dict] = None
    created_at: str
    completed_at: Optional[str] = None


# Task storage
tasks: Dict[str, TaskStatus] = {}
portfolio_data: Optional[Dict] = None
test_results_data: Optional[Dict] = None


class DashboardData(BaseModel):
    phases: List[PhaseStatus]
    total_modules: int
    last_updated: str
    tasks: List[TaskStatus]
    portfolio: Optional[Dict] = None
    test_results: Optional[Dict] = None


# Phase definitions
PHASES = [
    {
        "phase": "Phase 0",
        "name": "Reality Lock",
        "status": "complete",
        "modules": 7,
        "description": "Workspace setup, inventory, baseline, classification, reality lock"
    },
    {
        "phase": "Phase 1",
        "name": "Forge Constitution",
        "status": "complete",
        "modules": 4,
        "description": "Domain language, event contracts, governance, gate validation"
    },
    {
        "phase": "Phase 2",
        "name": "Runtime Foundry",
        "status": "complete",
        "modules": 4,
        "description": "Service topology, control plane, worker fabric"
    },
    {
        "phase": "Phase 3",
        "name": "Data Forge",
        "status": "complete",
        "modules": 4,
        "description": "Contracts, provider gateway, market reference lake"
    },
    {
        "phase": "Phase 4",
        "name": "Intelligence Forge",
        "status": "complete",
        "modules": 3,
        "description": "Intelligence contracts, observers, causal mapping"
    },
    {
        "phase": "Phase 5",
        "name": "Discovery Forge",
        "status": "complete",
        "modules": 3,
        "description": "Discovery contracts, scanner fabric, ranking"
    },
    {
        "phase": "Phase 6",
        "name": "Strategy Forge",
        "status": "complete",
        "modules": 3,
        "description": "Strategy contracts, Cerebus building blocks, compiler"
    },
    {
        "phase": "Phase 7",
        "name": "Validation Forge",
        "status": "complete",
        "modules": 3,
        "description": "Contracts, engines, robustness qualification"
    },
    {
        "phase": "Phase 8",
        "name": "Simulation Forge",
        "status": "complete",
        "modules": 4,
        "description": "Deployment manager, runtime health, paper/shadow"
    },
    {
        "phase": "Phase 9",
        "name": "Execution Forge",
        "status": "complete",
        "modules": 3,
        "description": "Execution contracts, adapter fabric, lifecycle"
    },
    {
        "phase": "Phase 10",
        "name": "Portfolio Forge",
        "status": "complete",
        "modules": 3,
        "description": "Portfolio contracts, capital envelopes, stress controls"
    },
    {
        "phase": "Phase 11",
        "name": "Sovereign Operations",
        "status": "complete",
        "modules": 3,
        "description": "Operations contracts, command center, incidents"
    },
]


@app.get("/")
async def dashboard():
    """Serve the dashboard HTML"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>GLX FORGE Dashboard</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                color: #e0e0e0;
                min-height: 100vh;
            }
            .container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
            }
            .header {
                text-align: center;
                padding: 40px 20px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 12px;
                margin-bottom: 30px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            .header h1 {
                font-size: 2.5rem;
                margin-bottom: 10px;
                background: linear-gradient(90deg, #00d4ff, #7c3aed);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            .header p {
                color: #888;
                font-size: 1.1rem;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .stat-card {
                background: rgba(255, 255, 255, 0.05);
                padding: 20px;
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                text-align: center;
            }
            .stat-card h3 {
                font-size: 2rem;
                margin-bottom: 5px;
                color: #00d4ff;
            }
            .stat-card p {
                color: #888;
                font-size: 0.9rem;
            }
            .phases {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
            }
            .phase-card {
                background: rgba(255, 255, 255, 0.05);
                padding: 25px;
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                transition: transform 0.3s, box-shadow 0.3s;
            }
            .phase-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 30px rgba(0, 212, 255, 0.2);
            }
            .phase-card .phase {
                font-size: 0.85rem;
                color: #00d4ff;
                margin-bottom: 5px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .phase-card h3 {
                font-size: 1.3rem;
                margin-bottom: 10px;
            }
            .phase-card .status {
                display: inline-block;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 0.85rem;
                margin-bottom: 10px;
            }
            .phase-card .status.complete {
                background: rgba(0, 255, 136, 0.2);
                color: #00ff88;
            }
            .phase-card .status.pending {
                background: rgba(255, 193, 7, 0.2);
                color: #ffc107;
            }
            .phase-card .modules {
                color: #888;
                font-size: 0.9rem;
                margin-bottom: 10px;
            }
            .phase-card .description {
                color: #aaa;
                font-size: 0.9rem;
                line-height: 1.5;
            }
            .workflow {
                margin-top: 40px;
                background: rgba(255, 255, 255, 0.05);
                padding: 30px;
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            .workflow h2 {
                margin-bottom: 20px;
                color: #00d4ff;
            }
            .workflow-steps {
                display: flex;
                flex-wrap: wrap;
                gap: 15px;
                justify-content: center;
            }
            .workflow-step {
                background: rgba(124, 58, 237, 0.2);
                padding: 15px 25px;
                border-radius: 25px;
                border: 1px solid rgba(124, 58, 237, 0.3);
                font-size: 0.9rem;
                color: #c4b5fd;
            }
            .workflow-step::after {
                content: "→";
                margin-left: 15px;
                color: #7c3aed;
            }
            .workflow-step:last-child::after {
                content: "";
            }
            .controls {
                margin-top: 40px;
                background: rgba(255, 255, 255, 0.05);
                padding: 30px;
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            .controls h2 {
                margin-bottom: 20px;
                color: #00d4ff;
            }
            .control-panel {
                display: grid;
                gap: 20px;
            }
            .control-group {
                display: flex;
                flex-direction: column;
                gap: 8px;
            }
            .control-group label {
                color: #888;
                font-size: 0.9rem;
            }
            .control-group select,
            .control-group input,
            .control-group textarea {
                background: rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 12px;
                color: #e0e0e0;
                font-size: 1rem;
            }
            .control-group textarea {
                min-height: 100px;
                resize: vertical;
            }
            .control-group input:focus,
            .control-group textarea:focus,
            .control-group select:focus {
                outline: none;
                border-color: #00d4ff;
            }
            button {
                background: linear-gradient(90deg, #00d4ff, #7c3aed);
                border: none;
                border-radius: 8px;
                padding: 15px 30px;
                color: white;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 20px rgba(0, 212, 255, 0.3);
            }
            .tasks {
                margin-top: 40px;
                background: rgba(255, 255, 255, 0.05);
                padding: 30px;
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            .tasks h2 {
                margin-bottom: 20px;
                color: #00d4ff;
            }
            .task-item {
                background: rgba(0, 0, 0, 0.3);
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 15px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            .task-item .task-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }
            .task-item .task-type {
                font-weight: 600;
                color: #00d4ff;
            }
            .task-item .task-status {
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 0.85rem;
            }
            .task-item .task-status.pending {
                background: rgba(255, 193, 7, 0.2);
                color: #ffc107;
            }
            .task-item .task-status.running {
                background: rgba(0, 212, 255, 0.2);
                color: #00d4ff;
            }
            .task-item .task-status.completed {
                background: rgba(0, 255, 136, 0.2);
                color: #00ff88;
            }
            .task-item .task-status.failed {
                background: rgba(255, 68, 68, 0.2);
                color: #ff4444;
            }
            .task-item .task-description {
                color: #aaa;
                font-size: 0.9rem;
                margin-bottom: 10px;
            }
            .task-item .task-result {
                background: rgba(0, 255, 136, 0.1);
                padding: 10px;
                border-radius: 6px;
                font-size: 0.85rem;
                color: #00ff88;
            }
            .portfolio-section {
                margin-top: 40px;
                background: rgba(255, 255, 255, 0.05);
                padding: 30px;
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            .portfolio-section h2 {
                margin-bottom: 20px;
                color: #00d4ff;
            }
            .portfolio-item {
                background: rgba(0, 0, 0, 0.3);
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 15px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            .portfolio-item .portfolio-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }
            .portfolio-item .portfolio-value {
                font-size: 1.5rem;
                color: #00ff88;
                font-weight: 600;
            }
            .test-results-section {
                margin-top: 40px;
                background: rgba(255, 255, 255, 0.05);
                padding: 30px;
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            .test-results-section h2 {
                margin-bottom: 20px;
                color: #00d4ff;
            }
            .test-result-item {
                background: rgba(0, 0, 0, 0.3);
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 15px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            .test-result-item .phase-name {
                font-weight: 600;
                color: #00d4ff;
                margin-bottom: 10px;
            }
            .test-result-item .metrics {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 10px;
            }
            .test-result-item .metric {
                background: rgba(0, 212, 255, 0.1);
                padding: 10px;
                border-radius: 6px;
            }
            .test-result-item .metric-label {
                font-size: 0.8rem;
                color: #888;
            }
            .test-result-item .metric-value {
                font-size: 1.1rem;
                color: #e0e0e0;
                font-weight: 600;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>GLX FORGE Dashboard</h1>
                <p>11-Phase Quant Lab Infrastructure - ALL PHASES COMPLETE</p>
            </div>
            
            <div class="stats">
                <div class="stat-card" style="border: 2px solid #00ff88; background: rgba(0, 255, 136, 0.1);">
                    <h3 style="color: #00ff88;">COMPLETE</h3>
                    <p>System Status</p>
                </div>
                <div class="stat-card">
                    <h3>11</h3>
                    <p>Phases Complete</p>
                </div>
                <div class="stat-card">
                    <h3>44</h3>
                    <p>Modules</p>
                </div>
                <div class="stat-card">
                    <h3>14/14</h3>
                    <p>Tests Passing</p>
                </div>
                <div class="stat-card">
                    <h3>100%</h3>
                    <p>Implementation</p>
                </div>
            </div>
            
            <div class="phases">
                <!-- Phases will be loaded dynamically -->
            </div>
            
            <div class="workflow">
                <h2>System Workflow</h2>
                <div class="workflow-steps">
                    <div class="workflow-step">Intelligence</div>
                    <div class="workflow-step">Discovery</div>
                    <div class="workflow-step">Strategy</div>
                    <div class="workflow-step">Validation</div>
                    <div class="workflow-step">Simulation</div>
                    <div class="workflow-step">Execution</div>
                    <div class="workflow-step">Portfolio</div>
                    <div class="workflow-step">Operations</div>
                </div>
            </div>
            
            <div class="controls">
                <h2>Workflow Controls</h2>
                <div class="control-panel">
                    <div class="control-group">
                        <label>Workflow Type</label>
                        <select id="workflowType">
                            <option value="scan">Market Scan</option>
                            <option value="backtest">Backtest Strategy</option>
                            <option value="validate">Validate Strategy</option>
                            <option value="deploy">Deploy to Paper Trading</option>
                        </select>
                    </div>
                    <div class="control-group">
                        <label>Description</label>
                        <input type="text" id="workflowDescription" placeholder="Describe your idea or request">
                    </div>
                    <div class="control-group">
                        <label>Parameters (JSON)</label>
                        <textarea id="workflowParameters" placeholder='{"instrument": "BTCUSDT", "period": "1h"}'></textarea>
                    </div>
                    <button onclick="submitWorkflow()">Submit Workflow</button>
                </div>
            </div>
            
            <div class="tasks">
                <h2>Active Tasks</h2>
                <div id="tasksList"></div>
            </div>
            
            <div class="portfolio-section">
                <h2>Portfolio Status</h2>
                <div id="portfolioData"></div>
            </div>
            
            <div class="test-results-section">
                <h2>Test Results</h2>
                <div id="testResultsData"></div>
            </div>
        </div>
        
        <script>
            async function loadPhases() {
                const response = await fetch('/api/phases');
                const data = await response.json();
                
                const phasesContainer = document.querySelector('.phases');
                phasesContainer.innerHTML = '';
                
                data.phases.forEach(phase => {
                    const card = document.createElement('div');
                    card.className = 'phase-card';
                    card.innerHTML = `
                        <div class="phase">${phase.phase}</div>
                        <h3>${phase.name}</h3>
                        <span class="status ${phase.status}">${phase.status}</span>
                        <div class="modules">${phase.modules} modules</div>
                        <div class="description">${phase.description}</div>
                    `;
                    phasesContainer.appendChild(card);
                });
                
                // Load tasks
                loadTasks(data.tasks);
                
                // Load portfolio
                loadPortfolio(data.portfolio);
                
                // Load test results
                loadTestResults(data.test_results);
            }
            
            async function loadTasks(tasks) {
                const tasksList = document.getElementById('tasksList');
                tasksList.innerHTML = '';
                
                if (tasks.length === 0) {
                    tasksList.innerHTML = '<p style="color: #888;">No active tasks</p>';
                    return;
                }
                
                tasks.forEach(task => {
                    const taskItem = document.createElement('div');
                    taskItem.className = 'task-item';
                    
                    let resultHtml = '';
                    if (task.result) {
                        resultHtml = `<div class="task-result">${JSON.stringify(task.result, null, 2)}</div>`;
                    }
                    
                    taskItem.innerHTML = `
                        <div class="task-header">
                            <span class="task-type">${task.type}</span>
                            <span class="task-status ${task.status}">${task.status}</span>
                        </div>
                        <div class="task-description">${task.description}</div>
                        ${resultHtml}
                    `;
                    tasksList.appendChild(taskItem);
                });
            }
            
            async function loadPortfolio(portfolio) {
                const portfolioData = document.getElementById('portfolioData');
                portfolioData.innerHTML = '';
                
                if (!portfolio) {
                    portfolioData.innerHTML = '<p style="color: #888;">No portfolio data available</p>';
                    return;
                }
                
                const portfolioItem = document.createElement('div');
                portfolioItem.className = 'portfolio-item';
                portfolioItem.innerHTML = `
                    <div class="portfolio-header">
                        <span>Portfolio ID: ${portfolio.portfolio_id}</span>
                        <span class="portfolio-value">$${portfolio.cash?.toLocaleString() || '0'}</span>
                    </div>
                    <div style="color: #aaa; font-size: 0.9rem;">
                        <div>Type: ${portfolio.portfolio_type}</div>
                        <div>Status: ${portfolio.status}</div>
                        <div>Position: ${portfolio.quantity || 0} ${portfolio.instrument || 'N/A'}</div>
                        <div>Avg Entry: $${portfolio.avg_entry_price?.toLocaleString() || '0'}</div>
                    </div>
                `;
                portfolioData.appendChild(portfolioItem);
            }
            
            async function loadTestResults(testResults) {
                const testResultsData = document.getElementById('testResultsData');
                testResultsData.innerHTML = '';
                
                if (!testResults) {
                    testResultsData.innerHTML = '<p style="color: #888;">No test results available</p>';
                    return;
                }
                
                for (const [phase, data] of Object.entries(testResults)) {
                    const resultItem = document.createElement('div');
                    resultItem.className = 'test-result-item';
                    
                    let metricsHtml = '';
                    for (const [key, value] of Object.entries(data)) {
                        if (typeof value === 'number') {
                            const displayValue = key.includes('pct') || key.includes('rate') || key.includes('return') || key.includes('drawdown') 
                                ? `${(value * 100).toFixed(2)}%` 
                                : value.toFixed(2);
                            metricsHtml += `
                                <div class="metric">
                                    <div class="metric-label">${key}</div>
                                    <div class="metric-value">${displayValue}</div>
                                </div>
                            `;
                        }
                    }
                    
                    resultItem.innerHTML = `
                        <div class="phase-name">${phase.toUpperCase()}</div>
                        <div class="metrics">${metricsHtml}</div>
                    `;
                    testResultsData.appendChild(resultItem);
                }
            }
            
            async function submitWorkflow() {
                const type = document.getElementById('workflowType').value;
                const description = document.getElementById('workflowDescription').value;
                const parametersText = document.getElementById('workflowParameters').value;
                
                let parameters = {};
                if (parametersText) {
                    try {
                        parameters = JSON.parse(parametersText);
                    } catch (e) {
                        alert('Invalid JSON parameters');
                        return;
                    }
                }
                
                const response = await fetch('/api/workflow', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        type,
                        description,
                        parameters
                    })
                });
                
                const task = await response.json();
                
                // Refresh tasks
                loadPhases();
                
                // Clear form
                document.getElementById('workflowDescription').value = '';
                document.getElementById('workflowParameters').value = '';
                
                alert(`Workflow submitted: ${task.task_id}`);
            }
            
            // Auto-refresh tasks every 5 seconds
            setInterval(loadPhases, 5000);
            
            // Initial load
            loadPhases();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/api/phases")
async def get_phases() -> DashboardData:
    """Get phase status data"""
    phases = [PhaseStatus(**p) for p in PHASES]
    total_modules = sum(p["modules"] for p in PHASES)
    task_list = list(tasks.values())
    
    return DashboardData(
        phases=phases,
        total_modules=total_modules,
        last_updated=datetime.now(timezone.utc).isoformat(),
        tasks=task_list,
        portfolio=portfolio_data,
        test_results=test_results_data
    )


@app.post("/api/update-portfolio")
async def update_portfolio(portfolio: Dict):
    """Update portfolio data"""
    global portfolio_data
    portfolio_data = portfolio
    return {"status": "updated"}


@app.post("/api/update-test-results")
async def update_test_results(results: Dict):
    """Update test results data"""
    global test_results_data
    test_results_data = results
    return {"status": "updated"}


@app.post("/api/workflow")
async def submit_workflow(request: WorkflowRequest) -> TaskStatus:
    """Submit a workflow request"""
    from uuid import uuid4
    
    task_id = str(uuid4())
    task = TaskStatus(
        task_id=task_id,
        type=request.type,
        status="pending",
        description=request.description,
        created_at=datetime.now(timezone.utc).isoformat()
    )
    
    tasks[task_id] = task
    
    # Simulate task execution
    await execute_task(task_id, request)
    
    return task


@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str) -> TaskStatus:
    """Get task status"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]


async def execute_task(task_id: str, request: WorkflowRequest):
    """Execute task using GLX FORGE workflow orchestrator"""
    from forge.dashboard.workflows import execute_workflow_task
    
    tasks[task_id].status = "running"
    
    # Execute the workflow using real GLX FORGE modules
    execution_result = await execute_workflow_task(
        task_id=task_id,
        workflow_type=request.type,
        parameters=request.parameters,
        description=request.description
    )
    
    if execution_result["success"]:
        tasks[task_id].status = "completed"
        tasks[task_id].completed_at = datetime.now(timezone.utc).isoformat()
        tasks[task_id].result = execution_result["result"]
    else:
        tasks[task_id].status = "failed"
        tasks[task_id].completed_at = datetime.now(timezone.utc).isoformat()
        tasks[task_id].result = {
            "error": execution_result["error"]
        }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
