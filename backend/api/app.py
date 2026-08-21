"""FastAPI application factory and static console mounting for RACE."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from backend.api.routes import router

app = FastAPI(
    title="RACE - Revenue Adaptive Control Engine API",
    description="AI-driven Revenue Recovery Decision Engine REST Service",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/", response_class=HTMLResponse)
def get_merchant_console():
    """Serves the standalone RACE Merchant Recovery Operations Console."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RACE - Revenue Adaptive Control Engine</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #0b0f19; color: #e2e8f0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        .card { background-color: #151d30; border: 1px solid #1e293b; }
        .badge-recovered { background-color: #064e3b; color: #6ee7b7; }
        .badge-escalated { background-color: #78350f; color: #fcd34d; }
        .badge-stopped { background-color: #374151; color: #9ca3af; }
    </style>
</head>
<body class="p-6">
    <div class="max-w-7xl mx-auto space-y-6">
        <!-- Header -->
        <header class="flex justify-between items-center pb-4 border-b border-slate-800">
            <div>
                <h1 class="text-3xl font-black tracking-tight text-white">RACE</h1>
                <p class="text-sm text-slate-400">Revenue Adaptive Control Engine — AI Revenue Recovery Console</p>
            </div>
            <div class="flex items-center space-x-3">
                <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-emerald-950 text-emerald-400 border border-emerald-800">
                    System: Closed-Loop Active
                </span>
                <button onclick="fetchBenchmark()" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded font-medium text-sm transition">
                    Run Live Benchmark
                </button>
            </div>
        </header>

        <!-- KPI Metrics Grid -->
        <section class="grid grid-cols-1 md:grid-cols-4 gap-4" id="kpi-grid">
            <div class="card p-5 rounded-lg">
                <p class="text-xs uppercase text-slate-400 font-semibold tracking-wider">Revenue at Risk</p>
                <h2 class="text-2xl font-bold text-red-400 mt-2" id="kpi-risk">Loading...</h2>
            </div>
            <div class="card p-5 rounded-lg">
                <p class="text-xs uppercase text-slate-400 font-semibold tracking-wider">Estimated Recoverable</p>
                <h2 class="text-2xl font-bold text-amber-400 mt-2" id="kpi-recoverable">Loading...</h2>
            </div>
            <div class="card p-5 rounded-lg">
                <p class="text-xs uppercase text-slate-400 font-semibold tracking-wider">Recovered Revenue</p>
                <h2 class="text-2xl font-bold text-emerald-400 mt-2" id="kpi-recovered">Loading...</h2>
            </div>
            <div class="card p-5 rounded-lg">
                <p class="text-xs uppercase text-slate-400 font-semibold tracking-wider">Incremental vs Baseline</p>
                <h2 class="text-2xl font-bold text-cyan-400 mt-2" id="kpi-incremental">Loading...</h2>
            </div>
        </section>

        <!-- Main Workspace: Queue & Detail -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Recovery Queue -->
            <div class="card rounded-lg p-5 lg:col-span-2 space-y-4">
                <div class="flex justify-between items-center">
                    <h3 class="font-bold text-lg text-white">Live Recovery Queue</h3>
                    <span class="text-xs text-slate-400" id="queue-count">Showing 50 cases</span>
                </div>
                <div class="overflow-x-auto max-h-[520px] overflow-y-auto">
                    <table class="w-full text-left text-sm text-slate-300">
                        <thead class="text-xs uppercase text-slate-400 bg-slate-900 sticky top-0">
                            <tr>
                                <th class="p-3">Case ID</th>
                                <th class="p-3">Amount</th>
                                <th class="p-3">Failure Class</th>
                                <th class="p-3">Strategy</th>
                                <th class="p-3">State</th>
                                <th class="p-3">Action</th>
                            </tr>
                        </thead>
                        <tbody id="cases-tbody" class="divide-y divide-slate-800">
                            <tr><td colspan="6" class="p-4 text-center text-slate-500">Loading cases...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Case Investigation & Decision Explorer -->
            <div class="card rounded-lg p-5 space-y-4">
                <h3 class="font-bold text-lg text-white">Decision & Audit Explorer</h3>
                <div id="case-detail-content" class="text-sm space-y-3 text-slate-300">
                    <p class="text-slate-500">Select a case from the recovery queue to view root cause diagnosis, ERV calculations, policy validations, and authoritative outcome verification.</p>
                </div>
            </div>
        </div>

        <!-- Benchmark Comparison Modal / Box -->
        <div id="benchmark-modal" class="card rounded-lg p-5 hidden space-y-4 border border-blue-900">
            <h3 class="font-bold text-lg text-white">Comparative Benchmark Results (Validation Split)</h3>
            <div id="benchmark-content" class="text-sm text-slate-300"></div>
        </div>
    </div>

    <script>
        async function loadOverview() {
            try {
                const res = await fetch('/api/v1/overview');
                const data = await res.json();
                document.getElementById('kpi-risk').innerText = 'INR ' + Number(data.revenue_at_risk_inr).toLocaleString();
                document.getElementById('kpi-recoverable').innerText = 'INR ' + Number(data.expected_recoverable_inr).toLocaleString();
                document.getElementById('kpi-recovered').innerText = 'INR ' + Number(data.actual_recovered_inr).toLocaleString();
                document.getElementById('kpi-incremental').innerText = '+' + 'INR ' + Number(data.incremental_recovered_inr).toLocaleString();
            } catch (e) {
                console.error(e);
            }
        }

        async function loadCases() {
            try {
                const res = await fetch('/api/v1/cases?limit=50');
                const cases = await res.json();
                const tbody = document.getElementById('cases-tbody');
                tbody.innerHTML = '';
                cases.forEach(c => {
                    const tr = document.createElement('tr');
                    tr.className = 'hover:bg-slate-800/50 cursor-pointer';
                    tr.onclick = () => loadCaseDetail(c.case_id);
                    
                    let badgeClass = 'badge-stopped';
                    if (c.current_state === 'RECOVERED') badgeClass = 'badge-recovered';
                    else if (c.current_state === 'ESCALATED') badgeClass = 'badge-escalated';

                    tr.innerHTML = `
                        <td class="p-3 font-mono font-medium text-blue-400">${c.case_id}</td>
                        <td class="p-3 font-semibold">INR ${c.amount.toFixed(2)}</td>
                        <td class="p-3 text-xs text-slate-400">${c.failure_class}</td>
                        <td class="p-3 font-mono text-xs">${c.selected_strategy}</td>
                        <td class="p-3"><span class="px-2 py-0.5 text-xs rounded ${badgeClass}">${c.current_state}</span></td>
                        <td class="p-3"><button class="text-xs text-blue-400 hover:underline">Investigate</button></td>
                    `;
                    tbody.appendChild(tr);
                });
                if (cases.length > 0) loadCaseDetail(cases[0].case_id);
            } catch (e) {
                console.error(e);
            }
        }

        async function loadCaseDetail(caseId) {
            try {
                const res = await fetch('/api/v1/cases/' + caseId);
                const data = await res.json();
                const container = document.getElementById('case-detail-content');
                const latestAudit = data.audit_trail && data.audit_trail.length > 0 ? data.audit_trail[data.audit_trail.length - 1] : null;

                container.innerHTML = `
                    <div class="p-3 bg-slate-900 rounded border border-slate-800">
                        <div class="text-xs text-slate-500 uppercase font-semibold">Selected Case</div>
                        <div class="text-lg font-bold text-white font-mono">${data.case_id}</div>
                        <div class="text-sm font-semibold text-emerald-400">Captured: INR ${data.summary.recovered_amount.toFixed(2)} / INR ${data.event.amount.toFixed(2)}</div>
                    </div>
                    <div class="space-y-1">
                        <div class="text-xs font-semibold uppercase text-slate-400">Root Cause Telemetry</div>
                        <p class="text-xs text-slate-300">${data.event.failure_reason} (Route: ${data.event.gateway_route_health})</p>
                    </div>
                    <div class="space-y-1">
                        <div class="text-xs font-semibold uppercase text-slate-400">Strategy & ERV Decision</div>
                        <p class="text-xs text-slate-300 font-mono">${latestAudit ? latestAudit.selected_action : 'N/A'}</p>
                        <p class="text-xs text-slate-400">${latestAudit ? latestAudit.selection_reason : ''}</p>
                    </div>
                    <div class="space-y-1">
                        <div class="text-xs font-semibold uppercase text-slate-400">Deterministic Safety Checks</div>
                        <div class="text-xs text-emerald-400 font-mono">Status: ${latestAudit ? latestAudit.policy_decision : 'N/A'} (Idempotency Key: Protected)</div>
                    </div>
                    <div class="space-y-1">
                        <div class="text-xs font-semibold uppercase text-slate-400">Decision Narrative</div>
                        <p class="text-xs text-slate-300 italic bg-slate-900/60 p-2 rounded">${data.explanation}</p>
                    </div>
                `;
            } catch (e) {
                console.error(e);
            }
        }

        async function fetchBenchmark() {
            const modal = document.getElementById('benchmark-modal');
            const content = document.getElementById('benchmark-content');
            modal.classList.remove('hidden');
            content.innerHTML = 'Running live comparative benchmark across Baselines A, B, C and RACE...';
            try {
                const res = await fetch('/api/v1/benchmark?split=validation');
                const data = await res.json();
                content.innerHTML = `
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 my-3">
                        <div class="p-3 bg-slate-900 rounded">
                            <div class="text-xs text-slate-400">Baseline A (Fixed Retry)</div>
                            <div class="text-base font-bold text-slate-300">INR ${data.baseline_a.total_recovered_revenue.toLocaleString()}</div>
                            <div class="text-xs text-slate-500">${data.baseline_a.recovery_rate_pct}% rec rate</div>
                        </div>
                        <div class="p-3 bg-slate-900 rounded">
                            <div class="text-xs text-slate-400">Baseline B (Rule-Based)</div>
                            <div class="text-base font-bold text-slate-300">INR ${data.baseline_b.total_recovered_revenue.toLocaleString()}</div>
                            <div class="text-xs text-slate-500">${data.baseline_b.recovery_rate_pct}% rec rate</div>
                        </div>
                        <div class="p-3 bg-slate-900 rounded">
                            <div class="text-xs text-slate-400">Baseline C (ML Ranking)</div>
                            <div class="text-base font-bold text-slate-300">INR ${data.baseline_c.total_recovered_revenue.toLocaleString()}</div>
                            <div class="text-xs text-slate-500">${data.baseline_c.recovery_rate_pct}% rec rate</div>
                        </div>
                        <div class="p-3 bg-emerald-950 border border-emerald-800 rounded">
                            <div class="text-xs text-emerald-400 font-bold">RACE Engine</div>
                            <div class="text-base font-bold text-emerald-300">INR ${data.race.actual_recovered_revenue.toLocaleString()}</div>
                            <div class="text-xs text-emerald-400 font-semibold">+INR ${data.race.incremental_revenue_vs_baseline_a.toLocaleString()} Uplift</div>
                        </div>
                    </div>
                `;
            } catch (e) {
                content.innerHTML = 'Error running benchmark: ' + e;
            }
        }

        window.onload = () => {
            loadOverview();
            loadCases();
        };
    </script>
</body>
</html>
"""
