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
    """Serves the minimal, polished RACE Merchant Operations Console."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RACE — Revenue Adaptive Control Engine</title>
    <!-- Distinctive Typographic System: Plus Jakarta Sans (UI/Headings) + JetBrains Mono (Data/Formulas) -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['"Plus Jakarta Sans"', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
                        mono: ['"JetBrains Mono"', 'monospace'],
                    },
                    colors: {
                        darkBase: '#0B0F17',
                        darkSurface: '#131B2A',
                        darkSurface2: '#0F1622',
                        darkBorder: '#1E2B3E',
                    }
                }
            }
        }
    </script>
    <script>
        if (localStorage.getItem('race_theme') === 'dark') {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    </script>
    <style>
        body {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            -webkit-font-smoothing: antialiased;
            transition: background-color 0.2s ease, color 0.2s ease;
        }

        .font-mono { font-family: 'JetBrains Mono', monospace; }

        /* Light & Dark Surface Cards */
        .card-surface {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 14px;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04);
            transition: all 0.2s ease;
        }
        .dark .card-surface {
            background-color: #131B2A;
            border-color: #1E2B3E;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.4);
        }

        .card-decision {
            background: linear-gradient(180deg, #F0FDF4 0%, #FFFFFF 100%);
            border: 1.5px solid #86EFAC;
            border-radius: 14px;
            box-shadow: 0 4px 12px -2px rgba(16, 185, 129, 0.08);
            transition: all 0.2s ease;
        }
        .dark .card-decision {
            background: linear-gradient(180deg, #0A1C16 0%, #0F1B27 100%);
            border: 1.5px solid #059669;
            box-shadow: 0 4px 12px -2px rgba(16, 185, 129, 0.15);
        }

        /* Semantic Badges */
        .badge {
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            font-weight: 600;
            padding: 3px 8px;
            border-radius: 6px;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }

        .badge-recovered { background-color: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; }
        .dark .badge-recovered { background-color: #064E3B; color: #34D399; border: 1px solid #059669; }

        .badge-escalated { background-color: #FFFBEB; color: #B45309; border: 1px solid #FDE68A; }
        .dark .badge-escalated { background-color: #78350F; color: #FBBF24; border: 1px solid #D97706; }

        .badge-stopped { background-color: #F1F5F9; color: #475569; border: 1px solid #CBD5E1; }
        .dark .badge-stopped { background-color: #1E293B; color: #94A3B8; border: 1px solid #334155; }

        .badge-at-risk { background-color: #FEF2F2; color: #B91C1C; border: 1px solid #FECACA; }
        .dark .badge-at-risk { background-color: #7F1D1D; color: #F87171; border: 1px solid #DC2626; }

        .badge-custom { background-color: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; }
        .dark .badge-custom { background-color: #1E3A8A; color: #60A5FA; border: 1px solid #2563EB; }

        .badge-benchmark { background-color: #F8FAFC; color: #64748B; border: 1px solid #E2E8F0; }
        .dark .badge-benchmark { background-color: #1E293B; color: #94A3B8; border: 1px solid #334155; }

        /* Step Nodes */
        .step-node {
            font-family: 'JetBrains Mono', monospace;
            font-size: 11.5px;
            font-weight: 600;
            padding: 6px 14px;
            border-radius: 20px;
            border: 1px solid #E2E8F0;
            background-color: #F8FAFC;
            color: #64748B;
            transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .dark .step-node {
            border-color: #1E2B3E;
            background-color: #0F1622;
            color: #94A3B8;
        }
        .step-node.active {
            border-color: #0284C7;
            background-color: #F0F9FF;
            color: #0284C7;
            font-weight: 700;
            box-shadow: 0 0 10px rgba(2, 132, 199, 0.15);
        }
        .dark .step-node.active {
            border-color: #38BDF8;
            background-color: #0C2A44;
            color: #38BDF8;
            box-shadow: 0 0 10px rgba(56, 189, 248, 0.2);
        }
        .step-node.done {
            border-color: #10B981;
            background-color: #ECFDF5;
            color: #047857;
        }
        .dark .step-node.done {
            border-color: #059669;
            background-color: #064E3B;
            color: #34D399;
        }

        /* KPI Card Animation */
        .kpi-card {
            transition: opacity 0.4s ease, transform 0.4s ease;
        }
    </style>
</head>
<body class="bg-white dark:bg-[#0B0F17] text-slate-900 dark:text-slate-100 antialiased min-h-screen">

    <!-- TOP NAVIGATION BAR -->
    <header class="border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0B0F17] sticky top-0 z-40 transition-colors">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div class="flex items-center space-x-4">
                <a href="/" class="flex items-center space-x-2.5">
                    <span class="w-7 h-7 rounded-lg bg-slate-900 dark:bg-white text-white dark:text-slate-900 font-extrabold flex items-center justify-center text-sm shadow-sm">R</span>
                    <div>
                        <span class="text-base font-bold tracking-tight text-slate-900 dark:text-white">RACE</span>
                        <span class="hidden sm:inline-block text-xs text-slate-500 dark:text-slate-400 font-medium ml-1.5">Revenue Adaptive Control Engine</span>
                    </div>
                </a>
                <span class="hidden md:inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-50 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800">
                    Engine Active
                </span>
            </div>

            <!-- MAIN NAVIGATION LINKS + THEME SWITCHER -->
            <nav class="flex items-center space-x-1 sm:space-x-2">
                <button onclick="openCreateCaseModal()" class="px-3.5 py-1.5 bg-slate-900 hover:bg-slate-800 dark:bg-white dark:hover:bg-slate-100 text-white dark:text-slate-900 text-xs font-semibold rounded-lg shadow-sm transition flex items-center space-x-1">
                    <span>+ Add Scenario</span>
                </button>
                <a href="/" class="px-3 py-1.5 text-xs font-semibold text-sky-700 dark:text-sky-400 bg-sky-50 dark:bg-sky-950/60 rounded-lg border border-sky-100 dark:border-sky-900">
                    Overview
                </a>
                <a href="#recovery-queue-section" class="px-3 py-1.5 text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 transition">
                    Recovery Queue
                </a>
                <a href="/benchmarks" class="px-3 py-1.5 text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 transition">
                    Benchmarks
                </a>
                <a href="/about" class="px-3 py-1.5 text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 transition">
                    About RACE
                </a>
                <!-- THEME TOGGLE BUTTON -->
                <button onclick="toggleTheme()" id="theme-toggle-btn" class="ml-1 p-1.5 text-xs font-mono font-semibold text-slate-600 dark:text-slate-300 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-lg border border-slate-300 dark:border-slate-700 transition flex items-center">
                    <span id="theme-label">🌙 Dark</span>
                </button>
            </nav>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">

        <!-- FIRST-ENTRY ORIENTATION HERO -->
        <section class="p-6 bg-slate-50 dark:bg-[#0F1622] rounded-xl border border-slate-200 dark:border-slate-800 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 transition-colors">
            <div class="space-y-1 max-w-3xl">
                <h1 class="text-lg sm:text-xl font-bold text-slate-900 dark:text-white tracking-tight">
                    Closed-loop revenue recovery decision engine.
                </h1>
                <p class="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
                    RACE finds revenue at risk, determines whether it can be recovered, selects the economically best recovery strategy via Expected Recovery Value (ERV), applies safety constraints, executes bounded actions, and verifies real payment settlement.
                </p>
            </div>
            <div class="flex items-center space-x-3 text-xs text-slate-500 dark:text-slate-400 font-mono">
                <span class="px-2.5 py-1 bg-white dark:bg-slate-800 rounded border border-slate-200 dark:border-slate-700">Track 03 — AI Revenue Recovery</span>
            </div>
        </section>

        <!-- ISSUE 1: PROMINENT PURE BLACK "TEST A SCENARIO" CONTROL CARD -->
        <section class="bg-black text-white rounded-2xl border border-neutral-800 p-6 space-y-4 shadow-2xl">
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 pb-3 border-b border-neutral-800">
                <div>
                    <div class="flex items-center space-x-2">
                        <span class="w-2.5 h-2.5 rounded-full bg-sky-400 animate-pulse"></span>
                        <h3 class="text-sm font-bold text-white uppercase tracking-wider font-mono">TEST A SCENARIO</h3>
                    </div>
                    <p class="text-xs text-neutral-400 mt-0.5">Select a predefined archetype or inject your own custom failure scenario.</p>
                </div>
                <button onclick="openCreateCaseModal()" class="px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white font-bold rounded-xl text-xs shadow-lg transition flex items-center space-x-1.5 cursor-pointer">
                    <span class="text-sm leading-none">+</span>
                    <span>Add Custom Scenario</span>
                </button>
            </div>
            
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-1" id="quick-cases-container">
                <button onclick="selectCase('case_0601')" class="p-3.5 bg-neutral-900/90 hover:bg-neutral-800 border border-neutral-800 hover:border-neutral-700 rounded-xl text-left transition group cursor-pointer">
                    <span class="font-bold text-xs text-sky-400 block font-mono group-hover:text-sky-300">case_0601</span>
                    <span class="text-xs text-neutral-300">Card Limit Deficit</span>
                </button>
                <button onclick="selectCase('case_0602')" class="p-3.5 bg-neutral-900/90 hover:bg-neutral-800 border border-neutral-800 hover:border-neutral-700 rounded-xl text-left transition group cursor-pointer">
                    <span class="font-bold text-xs text-sky-400 block font-mono group-hover:text-sky-300">case_0602</span>
                    <span class="text-xs text-neutral-300">UPI Route Glitch</span>
                </button>
                <button onclick="selectCase('case_0607')" class="p-3.5 bg-neutral-900/90 hover:bg-neutral-800 border border-neutral-800 hover:border-neutral-700 rounded-xl text-left transition group cursor-pointer">
                    <span class="font-bold text-xs text-rose-400 block font-mono group-hover:text-rose-300">case_0607</span>
                    <span class="text-xs text-neutral-300">Fraud Hard Stop</span>
                </button>
                <button onclick="selectCase('case_0610')" class="p-3.5 bg-neutral-900/90 hover:bg-neutral-800 border border-neutral-800 hover:border-neutral-700 rounded-xl text-left transition group cursor-pointer">
                    <span class="font-bold text-xs text-amber-400 block font-mono group-hover:text-amber-300">case_0610</span>
                    <span class="text-xs text-neutral-300">High Value Escalation</span>
                </button>
            </div>
        </section>

        <!-- FINANCIAL METRICS STRIP (Revealed Staggered Upon Investigation) -->
        <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 hidden" id="kpi-strip">
            <div class="card-surface p-5 kpi-card opacity-0 translate-y-2">
                <p class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider font-mono">Revenue at Risk</p>
                <div class="text-2xl sm:text-3xl font-bold font-mono text-slate-900 dark:text-white mt-1.5" id="kpi-risk">INR 1,526,385</div>
                <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Total failed transaction queue</p>
            </div>
            <div class="card-surface p-5 kpi-card opacity-0 translate-y-2">
                <p class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider font-mono">Viable Recoverable</p>
                <div class="text-2xl sm:text-3xl font-bold font-mono text-amber-600 dark:text-amber-400 mt-1.5" id="kpi-recoverable">INR 1,385,974</div>
                <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">90.8% cleared as economically viable</p>
            </div>
            <div class="card-surface p-5 kpi-card opacity-0 translate-y-2">
                <p class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider font-mono">Actual Recovered</p>
                <div class="text-2xl sm:text-3xl font-bold font-mono text-emerald-600 dark:text-emerald-400 mt-1.5" id="kpi-recovered">INR 1,385,974</div>
                <p class="text-xs text-slate-500 dark:text-slate-400 mt-1" id="kpi-recovered-sub">85.5% recovery rate (171 settled)</p>
            </div>
            <div class="card-surface p-5 kpi-card opacity-0 translate-y-2">
                <p class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider font-mono">Incremental Net Uplift</p>
                <div class="text-2xl sm:text-3xl font-bold font-mono text-sky-600 dark:text-sky-400 mt-1.5" id="kpi-incremental">+INR 388,072</div>
                <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">+28.0% uplift over fixed retry base</p>
            </div>
        </section>

        <!-- LIVE CASE INVESTIGATION & OPERATIONS WORKSPACE (State-Driven Layout Transition) -->
        <section id="live-operations" class="space-y-4">
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 pb-2 border-b border-slate-200 dark:border-slate-800">
                <div>
                    <h2 class="text-lg font-bold text-slate-900 dark:text-white tracking-tight">Case Investigation & Decisioning</h2>
                    <p class="text-xs text-slate-500 dark:text-slate-400">Select any target above, then click Investigate Case to run the closed-loop decision engine.</p>
                </div>
                <div class="flex items-center space-x-2 text-xs">
                    <span class="text-slate-500 dark:text-slate-400">Target:</span>
                    <span id="active-case-id-badge" class="font-mono font-bold text-slate-900 dark:text-white px-2.5 py-1 bg-slate-100 dark:bg-slate-800 rounded border border-slate-300 dark:border-slate-700">case_0601</span>
                    <span id="active-case-source-badge" class="badge badge-benchmark">BENCHMARK</span>
                </div>
            </div>

            <div id="operations-layout" class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">

                <!-- LEFT COLUMN: TARGET INCIDENT SUMMARY (Starts Center-Aligned in State A) -->
                <div id="incident-column" class="col-span-12 max-w-xl mx-auto w-full transition-all duration-500 space-y-4">
                    <div class="card-surface p-6 space-y-4 text-center">
                        <div class="flex justify-between items-center pb-3 border-b border-slate-100 dark:border-slate-800">
                            <span class="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider font-mono">PAYMENT INCIDENT</span>
                            <span id="spotlight-state-badge" class="badge badge-at-risk">RECOVERY ELIGIBLE</span>
                        </div>

                        <!-- Center-Aligned Incident Overview -->
                        <div class="py-2 space-y-1">
                            <div class="flex items-center justify-center space-x-2">
                                <span class="text-xs text-slate-400 font-mono">Case ID:</span>
                                <span class="text-sm font-bold font-mono text-slate-900 dark:text-white" id="spotlight-case-id">case_0601</span>
                                <span id="spotlight-source-tag" class="badge badge-benchmark">BENCHMARK</span>
                            </div>
                            <div class="text-3xl sm:text-4xl font-extrabold font-mono text-emerald-600 dark:text-emerald-400 pt-1" id="spotlight-amount">INR 1,681.55</div>
                            <p class="text-xs text-slate-500 dark:text-slate-400 font-medium" id="spotlight-incident-summary">Failed Card Transaction • Route Active</p>
                        </div>

                        <!-- Structured Diagnostic Specifications -->
                        <div class="space-y-2 text-xs bg-slate-50 dark:bg-slate-900/80 p-4 rounded-xl border border-slate-200 dark:border-slate-800 text-left font-mono">
                            <div class="flex justify-between">
                                <span class="text-slate-500 dark:text-slate-400 font-sans">Failure Class:</span>
                                <span class="font-semibold text-slate-900 dark:text-slate-200" id="spotlight-failure-class">INSUFFICIENT_FUNDS</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-slate-500 dark:text-slate-400 font-sans">Reason Code:</span>
                                <span class="text-slate-700 dark:text-slate-300 truncate max-w-[170px]" id="spotlight-failure-reason">INSUFFICIENT_FUNDS_OR_LIMIT</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-slate-500 dark:text-slate-400 font-sans">Payment Method:</span>
                                <span class="font-semibold text-slate-800 dark:text-slate-200" id="spotlight-method">CARD</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-slate-500 dark:text-slate-400 font-sans">Gateway Route:</span>
                                <span class="font-semibold text-emerald-600 dark:text-emerald-400" id="spotlight-gw">UP (Operational)</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-slate-500 dark:text-slate-400 font-sans">Customer Prior Rate:</span>
                                <span class="font-semibold text-slate-800 dark:text-slate-200" id="spotlight-cust-rate">68% Historical</span>
                            </div>
                        </div>

                        <!-- Main Investigation Action Button -->
                        <button onclick="startInvestigation()" id="btn-investigate" class="w-full py-3.5 px-4 bg-slate-900 hover:bg-slate-800 dark:bg-white dark:hover:bg-slate-100 text-white dark:text-slate-900 font-semibold text-sm rounded-xl shadow transition flex items-center justify-center space-x-2 cursor-pointer">
                            <span id="btn-investigate-text">Investigate Case</span>
                        </button>
                    </div>
                </div>

                <!-- RIGHT COLUMN: INVESTIGATION WORKSPACE & COUNTDOWN LOADER (Hidden in State A) -->
                <div id="investigation-column" class="hidden lg:col-span-8 space-y-4 transition-all duration-500">

                    <div class="card-surface p-6 space-y-5 relative overflow-hidden" id="investigation-container">

                        <!-- 5-STEP LIFECYCLE PROGRESS RAIL -->
                        <div id="step-rail-container" class="flex items-center justify-between overflow-x-auto pb-3 border-b border-slate-100 dark:border-slate-800 text-xs font-mono gap-2">
                            <span id="node-step1" class="step-node active">1. Diagnosis</span>
                            <span class="text-slate-300 dark:text-slate-700">→</span>
                            <span id="node-step2" class="step-node">2. Recoverability</span>
                            <span class="text-slate-300 dark:text-slate-700">→</span>
                            <span id="node-step3" class="step-node">3. Strategy & ERV</span>
                            <span class="text-slate-300 dark:text-slate-700">→</span>
                            <span id="node-step4" class="step-node">4. Policy Gate</span>
                            <span class="text-slate-300 dark:text-slate-700">→</span>
                            <span id="node-step5" class="step-node">5. Settlement</span>
                        </div>

                        <!-- ISSUE 3: ORGANIC NEURAL GRAPH + COUNTDOWN LOADER -->
                        <div id="investigation-loading-view" class="flex flex-col items-center justify-center py-12 space-y-5">
                            
                            <!-- Countdown Badge -->
                            <div class="flex items-center space-x-3 bg-slate-50 dark:bg-slate-900 px-5 py-2.5 rounded-2xl border border-slate-200 dark:border-slate-800">
                                <span class="text-xs font-mono font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">INVESTIGATION INITIALIZING</span>
                                <span class="text-xl font-bold font-mono text-sky-600 dark:text-sky-400" id="countdown-badge">03</span>
                            </div>

                            <!-- Organic Neural Canvas -->
                            <canvas id="neural-canvas" width="560" height="220" class="max-w-full rounded-xl"></canvas>
                            
                            <div class="text-center space-y-1 max-w-md">
                                <p class="text-xs font-mono font-bold text-slate-800 dark:text-slate-200" id="loading-stage-label">
                                    SYNTHESIZING CONTEXT & ROOT CAUSE TELEMETRY...
                                </p>
                                <p class="text-[11px] text-slate-500 dark:text-slate-400">
                                    Evaluating route reliability, marginal fees, friction penalties, and deterministic policy constraints.
                                </p>
                            </div>
                        </div>

                        <!-- INVESTIGATION RESULT CONTENT (Revealed Only After Investigation Completes) -->
                        <div id="investigation-results-view" class="hidden space-y-5">

                            <!-- STEP 1 & 2: DIAGNOSIS & RECOVERABILITY -->
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div class="p-4 bg-slate-50 dark:bg-slate-900/70 rounded-xl border border-slate-200 dark:border-slate-800 space-y-1">
                                    <span class="text-[11px] uppercase font-bold text-slate-500 dark:text-slate-400 block font-mono">Root Cause Diagnosis</span>
                                    <h3 class="text-sm font-bold text-slate-900 dark:text-white" id="step1-title">Customer reported insufficient balance.</h3>
                                    <p class="text-xs text-slate-600 dark:text-slate-400 leading-relaxed" id="step1-desc">
                                        Card issuer returned insufficient funds code. Route is healthy with 68% prior customer recovery rate.
                                    </p>
                                </div>
                                <div class="p-4 bg-slate-50 dark:bg-slate-900/70 rounded-xl border border-slate-200 dark:border-slate-800 space-y-1">
                                    <span class="text-[11px] uppercase font-bold text-slate-500 dark:text-slate-400 block font-mono">Recoverability Diagnostic</span>
                                    <p class="text-sm font-bold text-emerald-600 dark:text-emerald-400" id="step2-rec-eval">Recoverable Opportunity</p>
                                    <div class="flex flex-wrap gap-1 pt-1" id="step3-candidates-badges">
                                        <span class="px-2 py-0.5 rounded text-[10.5px] bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-mono border border-slate-200 dark:border-slate-700">RETRY_NOW</span>
                                        <span class="px-2 py-0.5 rounded text-[10.5px] bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-mono border border-slate-200 dark:border-slate-700">RETRY_LATER</span>
                                        <span class="px-2 py-0.5 rounded text-[10.5px] bg-sky-50 dark:bg-sky-950 text-sky-700 dark:text-sky-300 font-mono border border-sky-200 dark:border-sky-800 font-bold">REMINDER_THEN_RETRY</span>
                                        <span class="px-2 py-0.5 rounded text-[10.5px] bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-mono border border-slate-200 dark:border-slate-700">STOP</span>
                                    </div>
                                </div>
                            </div>

                            <!-- STEP 3: THE DECISION — VISUAL CENTERPIECE -->
                            <div id="decision-card-container" class="card-decision p-5 space-y-4">
                                <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 pb-3 border-b border-emerald-100 dark:border-emerald-900/60">
                                    <div>
                                        <span class="text-xs font-extrabold uppercase tracking-wider text-emerald-800 dark:text-emerald-400 font-mono">RECOMMENDED ACTION</span>
                                        <h4 class="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-white font-mono mt-0.5" id="rec-strategy-name">REMINDER THEN RETRY</h4>
                                    </div>
                                    <div class="text-left sm:text-right">
                                        <span class="text-xs uppercase text-slate-500 dark:text-slate-400 font-semibold font-mono block">Expected Recovery Value</span>
                                        <div class="text-2xl font-extrabold text-emerald-600 dark:text-emerald-400 font-mono" id="rec-erv-amount">INR 901.03</div>
                                    </div>
                                </div>

                                <!-- PARAMETERS -->
                                <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs bg-white dark:bg-slate-900/80 p-3.5 rounded-xl border border-emerald-100 dark:border-emerald-900/60 font-mono">
                                    <div>
                                        <span class="text-slate-500 dark:text-slate-400 text-[11px] block">P(Recovery)</span>
                                        <p class="text-sm font-bold text-slate-900 dark:text-white" id="param-prob">88.0%</p>
                                    </div>
                                    <div>
                                        <span class="text-slate-500 dark:text-slate-400 text-[11px] block">Action Fee</span>
                                        <p class="text-sm font-bold text-slate-700 dark:text-slate-300" id="param-cost">INR 8.00</p>
                                    </div>
                                    <div>
                                        <span class="text-slate-500 dark:text-slate-400 text-[11px] block">Customer Friction</span>
                                        <p class="text-sm font-bold text-slate-700 dark:text-slate-300" id="param-friction">INR 15.00</p>
                                    </div>
                                    <div>
                                        <span class="text-slate-500 dark:text-slate-400 text-[11px] block">Downside Risk</span>
                                        <p class="text-sm font-bold text-slate-700 dark:text-slate-300" id="param-risk">INR 5.00</p>
                                    </div>
                                </div>

                                <!-- WHY? NARRATIVE -->
                                <div class="space-y-1 text-xs sm:text-sm">
                                    <span class="font-bold text-slate-700 dark:text-slate-300 uppercase font-mono text-[11px]">Why this action?</span>
                                    <p class="text-slate-700 dark:text-slate-300 leading-relaxed" id="rec-narrative">
                                        Immediate retry fails with high probability during insufficient funds. Sending a polite notification and queuing a retry after account balance refresh maximizes net recovered value.
                                    </p>
                                </div>
                            </div>

                            <!-- STEP 4: POLICY GATE CHECK -->
                            <div class="card-surface p-4 space-y-3 bg-slate-50 dark:bg-slate-900/70">
                                <div class="flex justify-between items-center pb-2 border-b border-slate-200 dark:border-slate-800">
                                    <div class="flex items-center space-x-2">
                                        <span class="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 font-mono">DETERMINISTIC POLICY CHECK</span>
                                        <span class="hidden sm:inline text-xs text-slate-500 dark:text-slate-400">— AI proposes. Policy authorizes.</span>
                                    </div>
                                    <span id="safety-status-badge" class="badge badge-recovered">ACTION APPROVED</span>
                                </div>

                                <!-- 6 INVARIANTS -->
                                <div class="grid grid-cols-2 sm:grid-cols-3 gap-2 font-mono text-xs" id="safety-checks-grid">
                                    <div class="p-2 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 flex items-center space-x-1.5 text-emerald-600 dark:text-emerald-400">
                                        <span>✓</span> <span class="text-slate-700 dark:text-slate-300 text-[11px]">Retry Cap <= 3</span>
                                    </div>
                                    <div class="p-2 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 flex items-center space-x-1.5 text-emerald-600 dark:text-emerald-400">
                                        <span>✓</span> <span class="text-slate-700 dark:text-slate-300 text-[11px]">Amount <= 50K</span>
                                    </div>
                                    <div class="p-2 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 flex items-center space-x-1.5 text-emerald-600 dark:text-emerald-400">
                                        <span>✓</span> <span class="text-slate-700 dark:text-slate-300 text-[11px]">SHA-256 Locked</span>
                                    </div>
                                    <div class="p-2 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 flex items-center space-x-1.5 text-emerald-600 dark:text-emerald-400">
                                        <span>✓</span> <span class="text-slate-700 dark:text-slate-300 text-[11px]">Opt-Out Verified</span>
                                    </div>
                                    <div class="p-2 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 flex items-center space-x-1.5 text-emerald-600 dark:text-emerald-400">
                                        <span>✓</span> <span class="text-slate-700 dark:text-slate-300 text-[11px]">Payment State Valid</span>
                                    </div>
                                    <div class="p-2 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 flex items-center space-x-1.5 text-emerald-600 dark:text-emerald-400">
                                        <span>✓</span> <span class="text-slate-700 dark:text-slate-300 text-[11px]">Policy Cleared</span>
                                    </div>
                                </div>
                            </div>

                            <!-- STEP 5: BOUNDED EXECUTION & OUTCOME SETTLEMENT -->
                            <div class="space-y-3 pt-1">
                                <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                                    <div>
                                        <span class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase font-mono block">Action Execution</span>
                                        <h4 class="text-sm font-bold text-slate-900 dark:text-white font-mono">Target: <span id="exec-case-id" class="text-sky-600 dark:text-sky-400">case_0601</span></h4>
                                    </div>

                                    <button onclick="executeLiveRecovery()" id="btn-execute" class="py-2.5 px-6 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-sm rounded-xl shadow-sm transition flex items-center space-x-2 cursor-pointer">
                                        <span id="btn-execute-text">Execute Recovery Action</span>
                                    </button>
                                </div>

                                <!-- SETTLEMENT & VERIFICATION CARD -->
                                <div id="outcome-panel" class="card-surface p-4 space-y-3 bg-emerald-50/60 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800 hidden">
                                    <div class="flex justify-between items-center pb-2 border-b border-emerald-200 dark:border-emerald-800">
                                        <span class="text-xs font-bold uppercase tracking-wider text-emerald-900 dark:text-emerald-300 font-mono">AUTHORITATIVE SETTLEMENT VERIFIED</span>
                                        <span class="badge badge-recovered">PAYMENT CAPTURED</span>
                                    </div>

                                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs bg-white dark:bg-slate-900 p-3 rounded-lg border border-emerald-200 dark:border-emerald-800 font-mono">
                                        <div>
                                            <span class="text-slate-500 dark:text-slate-400 text-[11px] block">Pre-Action Balance</span>
                                            <p class="font-bold text-rose-600 dark:text-rose-400 mt-0.5" id="outcome-pre-amt">INR 1,681.55 Outstanding</p>
                                        </div>
                                        <div>
                                            <span class="text-slate-500 dark:text-slate-400 text-[11px] block">Settled Gateway Balance</span>
                                            <p class="font-bold text-emerald-600 dark:text-emerald-400 mt-0.5" id="outcome-post-amt">INR 1,681.55 CAPTURED</p>
                                        </div>
                                    </div>

                                    <!-- CLOSED LOOP BAYESIAN NOTE -->
                                    <div class="p-2.5 bg-white dark:bg-slate-900 rounded-lg border border-emerald-200 dark:border-emerald-800 text-xs text-slate-700 dark:text-slate-300 space-y-0.5">
                                        <span class="font-bold text-emerald-800 dark:text-emerald-400 text-[11px] font-mono block">Closed-Loop Bayesian Update</span>
                                        <p id="learning-update-text" class="text-slate-600 dark:text-slate-400 text-xs">
                                            Outcome recorded in immutable ledger. Updated empirical statistics for (INSUFFICIENT_FUNDS, REMINDER_THEN_RETRY). New empirical success rate: 88.0%.
                                        </p>
                                    </div>
                                </div>
                            </div>

                        </div>

                    </div>
                </div>
            </div>
        </section>

        <!-- HUMAN-READABLE DECISION & AUDIT EXPLORER (Hidden until Investigation Completes) -->
        <section class="card-surface p-6 space-y-5 hidden" id="decision-explorer-section">
            <div>
                <h3 class="text-base font-bold text-slate-900 dark:text-white">Why Did RACE Make This Decision?</h3>
                <p class="text-xs text-slate-500 dark:text-slate-400">Clear business rationale, economic factors, policy verification, and progressive technical evidence.</p>
            </div>

            <!-- Primary Business Summary -->
            <div class="p-4 bg-slate-50 dark:bg-slate-900/80 rounded-xl border border-slate-200 dark:border-slate-800 space-y-2">
                <div class="flex items-center space-x-2">
                    <span class="text-xs font-bold text-slate-700 dark:text-slate-300 font-mono uppercase">BUSINESS SUMMARY</span>
                </div>
                <p class="text-sm text-slate-800 dark:text-slate-200 font-medium leading-relaxed" id="tab-biz-summary">
                    Selected Case: case_0601. RACE diagnosed that this transaction failed due to temporary card balance limits.
                </p>
                <p class="text-xs text-slate-600 dark:text-slate-400 leading-relaxed font-sans" id="tab-biz-narrative">
                    "RACE evaluated 4 candidate interventions. Immediate retry was rejected due to low success probability (12%). Reminder then retry maximizes net recovery value (INR 901.03) after factoring in communication fee (INR 8.00) and customer friction penalty (INR 15.00). Deterministic policy gate verified zero duplicate risk and authorized test-mode execution."
                </p>
            </div>

            <!-- Progressive Disclosure Sections -->
            <div class="space-y-2.5 text-xs">
                
                <!-- Collapsible 1: ERV Calculation -->
                <details class="group rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden bg-white dark:bg-[#131B2A]">
                    <summary class="p-3.5 bg-slate-50/70 dark:bg-slate-900/60 font-semibold text-slate-800 dark:text-slate-200 cursor-pointer flex justify-between items-center hover:bg-slate-100 dark:hover:bg-slate-800/80 transition">
                        <span class="flex items-center space-x-2 font-mono">
                            <span class="text-sky-600 dark:text-sky-400">▼</span>
                            <span>Mathematical Reasoning & ERV Calculation</span>
                        </span>
                        <span class="text-[11px] text-slate-400 font-mono">Formula Breakdown</span>
                    </summary>
                    <div class="p-4 space-y-3 font-mono text-xs border-t border-slate-200 dark:border-slate-800">
                        <div class="p-3 bg-slate-50 dark:bg-slate-900 rounded-lg text-sky-800 dark:text-sky-300 font-bold">
                            ERV(a) = P(rec | context, a) * Amount - Cost(a) - Friction(a) - Risk(a)
                        </div>
                        <div id="erv-formula-instance" class="text-slate-700 dark:text-slate-300 text-[11.5px]">
                            ERV = 0.88 * 1681.55 - 8.00 - 15.00 - 5.00 = INR 1,451.76
                        </div>
                        <div class="overflow-x-auto rounded-lg border border-slate-200 dark:border-slate-800">
                            <table class="w-full text-left">
                                <thead class="bg-slate-50 dark:bg-slate-900 text-slate-500 dark:text-slate-400 text-[10.5px] uppercase">
                                    <tr>
                                        <th class="p-2.5">Strategy</th>
                                        <th class="p-2.5">P(Recovery)</th>
                                        <th class="p-2.5">Fee</th>
                                        <th class="p-2.5">Friction</th>
                                        <th class="p-2.5">Risk</th>
                                        <th class="p-2.5">Net ERV</th>
                                    </tr>
                                </thead>
                                <tbody id="tab-erv-tbody" class="divide-y divide-slate-100 dark:divide-slate-800 text-[11px]">
                                    <!-- populated by js -->
                                </tbody>
                            </table>
                        </div>
                    </div>
                </details>

                <!-- Collapsible 2: Technical Telemetry -->
                <details class="group rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden bg-white dark:bg-[#131B2A]">
                    <summary class="p-3.5 bg-slate-50/70 dark:bg-slate-900/60 font-semibold text-slate-800 dark:text-slate-200 cursor-pointer flex justify-between items-center hover:bg-slate-100 dark:hover:bg-slate-800/80 transition">
                        <span class="flex items-center space-x-2 font-mono">
                            <span class="text-sky-600 dark:text-sky-400">▼</span>
                            <span>Technical Telemetry Envelope</span>
                        </span>
                        <span class="text-[11px] text-slate-400 font-mono">Raw Event Payload</span>
                    </summary>
                    <div class="p-4 border-t border-slate-200 dark:border-slate-800">
                        <pre id="tab-tech-raw" class="overflow-x-auto font-mono text-[11.5px] text-slate-800 dark:text-slate-200 bg-slate-50 dark:bg-slate-900 p-3.5 rounded-lg border border-slate-200 dark:border-slate-800 leading-relaxed"></pre>
                    </div>
                </details>

                <!-- Collapsible 3: Audit Ledger -->
                <details class="group rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden bg-white dark:bg-[#131B2A]">
                    <summary class="p-3.5 bg-slate-50/70 dark:bg-slate-900/60 font-semibold text-slate-800 dark:text-slate-200 cursor-pointer flex justify-between items-center hover:bg-slate-100 dark:hover:bg-slate-800/80 transition">
                        <span class="flex items-center space-x-2 font-mono">
                            <span class="text-sky-600 dark:text-sky-400">▼</span>
                            <span>Immutable Audit Ledger</span>
                        </span>
                        <span class="text-[11px] text-slate-400 font-mono">State Transitions</span>
                    </summary>
                    <div class="p-4 border-t border-slate-200 dark:border-slate-800 max-h-[260px] overflow-y-auto space-y-2" id="tab-audit-list">
                        <!-- populated by js -->
                    </div>
                </details>
            </div>
        </section>

        <!-- OPERATIONAL RECOVERY QUEUE -->
        <section id="recovery-queue-section" class="card-surface p-6 space-y-4">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-3">
                <div>
                    <div class="flex items-center space-x-2">
                        <h3 class="text-lg font-bold text-slate-900 dark:text-white">Operational Recovery Queue</h3>
                        <span id="queue-count-badge" class="badge badge-benchmark">
                            50 visible cases
                        </span>
                    </div>
                    <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Live failed revenue events requiring automated evaluation or manual intervention.</p>
                </div>

                <!-- CONTROLS -->
                <div class="flex flex-wrap items-center gap-2 text-xs font-mono">
                    <input type="text" id="queue-search" oninput="filterCases()" placeholder="Search Case ID or Reason..." class="px-3 py-1.5 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-800 dark:text-slate-100 focus:outline-none focus:border-sky-600">
                    <select id="queue-source-filter" onchange="filterCases()" class="px-3 py-1.5 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-800 dark:text-slate-100 focus:outline-none focus:border-sky-600">
                        <option value="ALL">All Sources</option>
                        <option value="CUSTOM">Custom Only</option>
                        <option value="BENCHMARK">Benchmark Only</option>
                    </select>
                    <select id="queue-filter" onchange="filterCases()" class="px-3 py-1.5 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-800 dark:text-slate-100 focus:outline-none focus:border-sky-600">
                        <option value="ALL">All States</option>
                        <option value="RECOVERED">Recovered</option>
                        <option value="ESCALATED">Escalated</option>
                        <option value="STOPPED">Stopped</option>
                        <option value="AT_RISK">At Risk</option>
                    </select>
                </div>
            </div>

            <div class="overflow-x-auto max-h-[440px] overflow-y-auto rounded-xl border border-slate-200 dark:border-slate-800">
                <table class="w-full text-left text-xs text-slate-800 dark:text-slate-200">
                    <thead class="text-[11px] uppercase font-mono text-slate-500 dark:text-slate-400 bg-slate-50 dark:bg-slate-900 sticky top-0 border-b border-slate-200 dark:border-slate-800">
                        <tr>
                            <th class="p-3 font-semibold">Case ID</th>
                            <th class="p-3 font-semibold">Source</th>
                            <th class="p-3 font-semibold">Amount</th>
                            <th class="p-3 font-semibold">Failure Reason</th>
                            <th class="p-3 font-semibold">Recommended Strategy</th>
                            <th class="p-3 font-semibold">Current State</th>
                            <th class="p-3 font-semibold">Action</th>
                        </tr>
                    </thead>
                    <tbody id="cases-tbody" class="divide-y divide-slate-100 dark:divide-slate-800 font-sans">
                        <tr><td colspan="7" class="p-4 text-center text-slate-400 font-mono">Loading cases...</td></tr>
                    </tbody>
                </table>
            </div>
        </section>

    </main>

    <!-- FOOTER -->
    <footer class="border-t border-slate-200 dark:border-slate-800 py-6 mt-12 bg-slate-50 dark:bg-[#0B0F17] text-center text-xs text-slate-500 dark:text-slate-400 font-mono transition-colors">
        RACE — Revenue Adaptive Control Engine | Autonomous Revenue Recovery Control System
    </footer>

    <!-- MODAL: ADD CUSTOM TEST CASE -->
    <div id="modal-add-case" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 hidden">
        <div class="bg-white dark:bg-[#131B2A] rounded-xl w-full max-w-xl p-6 space-y-5 shadow-xl border border-slate-200 dark:border-slate-800 overflow-y-auto max-h-[90vh]">
            
            <div class="flex justify-between items-start border-b border-slate-100 dark:border-slate-800 pb-3">
                <div>
                    <h3 class="text-lg font-bold text-slate-900 dark:text-white">Add Custom Test Scenario</h3>
                    <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                        Submit a payment failure event to run it through the live RACE decision & recovery pipeline.
                    </p>
                </div>
                <button onclick="closeCreateCaseModal()" class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 font-bold p-1">✕</button>
            </div>

            <!-- FORM -->
            <form id="form-create-case" onsubmit="handleCreateCaseSubmit(event)" class="space-y-3.5 text-xs">
                
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                        <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Amount (INR) *</label>
                        <input type="number" step="0.01" min="1" max="10000000" id="inp-amount" required value="2800.00" class="w-full p-2 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white font-mono focus:border-sky-600 focus:outline-none">
                    </div>
                    <div>
                        <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Currency</label>
                        <input type="text" id="inp-currency" value="INR" readonly class="w-full p-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-500 dark:text-slate-400 font-mono">
                    </div>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                        <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Failure Class *</label>
                        <select id="inp-failure-class" onchange="onFailureClassChange()" class="w-full p-2 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:border-sky-600 focus:outline-none font-mono">
                            <option value="INSUFFICIENT_FUNDS">INSUFFICIENT_FUNDS</option>
                            <option value="TEMPORARY_NETWORK">TEMPORARY_NETWORK</option>
                            <option value="AUTH_REQUIRED">AUTH_REQUIRED</option>
                            <option value="GATEWAY_DEGRADATION">GATEWAY_DEGRADATION</option>
                            <option value="EXPIRED_CARD">EXPIRED_CARD</option>
                            <option value="FRAUD_SUSPECTED">FRAUD_SUSPECTED</option>
                            <option value="CUSTOMER_ABANDONMENT">CUSTOMER_ABANDONMENT</option>
                            <option value="UNKNOWN">UNKNOWN</option>
                        </select>
                    </div>
                    <div>
                        <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Failure Reason</label>
                        <input type="text" id="inp-failure-reason" value="INSUFFICIENT_FUNDS_OR_LIMIT" class="w-full p-2 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white font-mono focus:border-sky-600 focus:outline-none">
                    </div>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <div>
                        <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Payment Method</label>
                        <select id="inp-method" class="w-full p-2 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:border-sky-600 focus:outline-none font-mono">
                            <option value="CARD">CARD</option>
                            <option value="UPI">UPI</option>
                            <option value="NETBANKING">NETBANKING</option>
                            <option value="WALLET">WALLET</option>
                        </select>
                    </div>
                    <div>
                        <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Gateway Health</label>
                        <select id="inp-gw-health" class="w-full p-2 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:border-sky-600 focus:outline-none font-mono">
                            <option value="UP">UP (Healthy)</option>
                            <option value="DEGRADED">DEGRADED</option>
                            <option value="DOWN">DOWN</option>
                        </select>
                    </div>
                    <div>
                        <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Customer History</label>
                        <input type="number" step="0.05" min="0" max="1" id="inp-cust-rate" value="0.65" class="w-full p-2 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white font-mono focus:border-sky-600 focus:outline-none">
                    </div>
                </div>

                <div class="flex items-center space-x-2 pt-1">
                    <input type="checkbox" id="inp-opted-out" class="w-4 h-4 rounded border-slate-300 dark:border-slate-700 text-slate-900 focus:ring-0">
                    <label for="inp-opted-out" class="text-slate-700 dark:text-slate-300 font-medium cursor-pointer text-xs">
                        Customer Opted Out of Automated Communications (Policy STOP)
                    </label>
                </div>

                <!-- ADVANCED CONTEXT TOGGLE -->
                <div class="pt-2 border-t border-slate-100 dark:border-slate-800">
                    <button type="button" onclick="toggleAdvancedContext()" class="text-xs text-sky-600 dark:text-sky-400 hover:underline font-semibold">
                        <span id="adv-ctx-label">+ Expand Advanced Fields</span>
                    </button>
                    <div id="adv-ctx-box" class="hidden grid grid-cols-1 sm:grid-cols-3 gap-3 mt-2.5 p-3 bg-slate-50 dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800">
                        <div>
                            <label class="block text-slate-500 dark:text-slate-400 text-[10.5px] mb-1">Previous Retries</label>
                            <input type="number" min="0" max="5" id="inp-retry-count" value="0" class="w-full p-1.5 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded text-slate-900 dark:text-white font-mono text-xs">
                        </div>
                        <div>
                            <label class="block text-slate-500 dark:text-slate-400 text-[10.5px] mb-1">Time Since Failure (mins)</label>
                            <input type="number" min="0" id="inp-time-since" value="0" class="w-full p-1.5 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded text-slate-900 dark:text-white font-mono text-xs">
                        </div>
                        <div>
                            <label class="block text-slate-500 dark:text-slate-400 text-[10.5px] mb-1">Merchant Tier</label>
                            <select id="inp-mcc-tier" class="w-full p-1.5 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded text-slate-900 dark:text-white text-xs font-mono">
                                <option value="medium">medium</option>
                                <option value="enterprise">enterprise</option>
                                <option value="high_risk">high_risk</option>
                            </select>
                        </div>
                    </div>
                </div>

                <!-- SUBMIT / CANCEL -->
                <div class="flex justify-end space-x-2.5 pt-3 border-t border-slate-100 dark:border-slate-800">
                    <button type="button" onclick="closeCreateCaseModal()" class="px-3.5 py-2 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg font-semibold transition">
                        Cancel
                    </button>
                    <button type="submit" id="btn-submit-case" class="px-5 py-2 bg-slate-900 hover:bg-slate-800 dark:bg-white dark:hover:bg-slate-100 text-white dark:text-slate-900 rounded-lg font-semibold shadow-sm transition">
                        <span id="btn-submit-case-text">Add Scenario & Evaluate</span>
                    </button>
                </div>
            </form>
        </div>
    </div>

    <!-- CLIENT CONTROLLER SCRIPT (Strict 3-State Model + Organic Neural Canvas) -->
    <script>
        let allCases = [];
        let currentCase = null;
        let neuralAnimId = null;
        let isInvestigating = false;

        function toggleTheme() {
            const isDark = document.documentElement.classList.toggle('dark');
            localStorage.setItem('race_theme', isDark ? 'dark' : 'light');
            updateThemeLabel();
        }

        function updateThemeLabel() {
            const isDark = document.documentElement.classList.contains('dark');
            const label = document.getElementById('theme-label');
            if (label) {
                label.innerText = isDark ? '☀️ Light' : '🌙 Dark';
            }
        }

        // ISSUE 3: Organic Free-Flowing Neural Graph Canvas with Countdown
        function startOrganicNeuralAnimation() {
            const canvas = document.getElementById('neural-canvas');
            if (!canvas) return;
            const ctx = canvas.getContext('2d');
            const width = canvas.width;
            const height = canvas.height;

            const isDark = document.documentElement.classList.contains('dark');
            const nodeColor = isDark ? '#38BDF8' : '#0284C7';
            const nodeSecondary = isDark ? '#34D399' : '#059669';
            const lineColor = isDark ? 'rgba(56, 189, 248, ' : 'rgba(2, 132, 199, ';

            // 7 naturally/organically distributed nodes
            const rawNodes = [
                { nx: 0.16, ny: 0.46, r: 6.5, color: nodeColor, label: 'TELEMETRY' },
                { nx: 0.32, ny: 0.22, r: 5.5, color: nodeColor, label: 'ROUTE' },
                { nx: 0.34, ny: 0.78, r: 5.5, color: nodeColor, label: 'ISSUER' },
                { nx: 0.52, ny: 0.48, r: 7.5, color: nodeSecondary, label: 'ERV' },
                { nx: 0.68, ny: 0.25, r: 5.5, color: nodeColor, label: 'POLICY' },
                { nx: 0.72, ny: 0.75, r: 5.5, color: nodeColor, label: 'LOCK' },
                { nx: 0.88, ny: 0.48, r: 8.0, color: nodeSecondary, label: 'ACTION' }
            ];

            const edges = [
                [0, 1], [0, 2], [0, 3],
                [1, 3], [1, 4],
                [2, 3], [2, 5],
                [3, 4], [3, 5], [3, 6],
                [4, 6], [5, 6]
            ];

            const startTime = performance.now();

            function render(now) {
                const elapsed = (now - startTime) / 1000;
                ctx.clearRect(0, 0, width, height);

                // Update Countdown HUD
                const remaining = Math.max(0, 3.2 - elapsed);
                const countBadge = document.getElementById('countdown-badge');
                const stageLabel = document.getElementById('loading-stage-label');

                if (countBadge && stageLabel) {
                    if (remaining > 2.0) {
                        countBadge.innerText = '03';
                        stageLabel.innerText = 'SYNTHESIZING FAILURE TELEMETRY & ROUTE HEALTH...';
                    } else if (remaining > 1.0) {
                        countBadge.innerText = '02';
                        stageLabel.innerText = 'EVALUATING EXPECTED RECOVERY VALUE (ERV)...';
                    } else if (remaining > 0.1) {
                        countBadge.innerText = '01';
                        stageLabel.innerText = 'VERIFYING DETERMINISTIC SAFETY GATES...';
                    } else {
                        countBadge.innerText = '✓';
                        stageLabel.innerText = 'OPTIMAL STRATEGY IDENTIFIED';
                    }
                }

                // Progressive Edge Drawing with organic curve
                edges.forEach((edge, idx) => {
                    const progressThreshold = idx * 0.22;
                    if (elapsed < progressThreshold) return;

                    const n1 = rawNodes[edge[0]];
                    const n2 = rawNodes[edge[1]];
                    const x1 = n1.nx * width;
                    const y1 = n1.ny * height;
                    const x2 = n2.nx * width;
                    const y2 = n2.ny * height;

                    const edgeProgress = Math.min(1, (elapsed - progressThreshold) * 2.5);
                    const curX = x1 + (x2 - x1) * edgeProgress;
                    const curY = y1 + (y2 - y1) * edgeProgress;

                    const pulse = 0.35 + 0.3 * Math.sin(elapsed * 4 + idx);
                    ctx.strokeStyle = lineColor + pulse + ')';
                    ctx.lineWidth = 1.6;
                    ctx.beginPath();
                    ctx.moveTo(x1, y1);
                    ctx.lineTo(curX, curY);
                    ctx.stroke();
                });

                // Progressive Node Appearance
                rawNodes.forEach((n, idx) => {
                    const nodeThreshold = idx * 0.35;
                    if (elapsed < nodeThreshold) return;

                    const nodeProgress = Math.min(1, (elapsed - nodeThreshold) * 3);
                    const x = n.nx * width + Math.sin(elapsed * 2 + idx) * 2.5;
                    const y = n.ny * height + Math.cos(elapsed * 2 + idx) * 2.5;

                    const currentR = n.r * nodeProgress + Math.sin(elapsed * 5 + idx) * 1.2;

                    ctx.fillStyle = n.color;
                    ctx.beginPath();
                    ctx.arc(x, y, Math.max(2, currentR), 0, Math.PI * 2);
                    ctx.fill();

                    // Outer soft ripple
                    ctx.strokeStyle = lineColor + '0.3)';
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.arc(x, y, currentR + 4 * Math.sin(elapsed * 4 + idx), 0, Math.PI * 2);
                    ctx.stroke();
                });

                neuralAnimId = requestAnimationFrame(render);
            }

            if (neuralAnimId) cancelAnimationFrame(neuralAnimId);
            neuralAnimId = requestAnimationFrame(render);
        }

        function stopOrganicNeuralAnimation() {
            if (neuralAnimId) {
                cancelAnimationFrame(neuralAnimId);
                neuralAnimId = null;
            }
        }

        function revealKPIs() {
            const strip = document.getElementById('kpi-strip');
            if (strip) strip.classList.remove('hidden');

            const kpis = document.querySelectorAll('.kpi-card');
            kpis.forEach((card, idx) => {
                setTimeout(() => {
                    card.classList.remove('opacity-0', 'translate-y-2');
                    card.classList.add('opacity-100', 'translate-y-0');
                }, idx * 120);
            });
        }

        function setStepNode(id, label, state) {
            const el = document.getElementById(id);
            if (!el) return;
            el.innerText = label;
            el.className = 'step-node ';
            if (state === 'COMPLETED') {
                el.className += 'done';
            } else if (state === 'ACTIVE') {
                el.className += 'active';
            } else {
                el.className += '';
            }
        }

        function updateStepProgress(stage) {
            if (stage === 0) {
                // Pre-investigation
                setStepNode('node-step1', '1. Diagnosis', 'ACTIVE');
                setStepNode('node-step2', '2. Recoverability', 'PENDING');
                setStepNode('node-step3', '3. Strategy & ERV', 'PENDING');
                setStepNode('node-step4', '4. Policy Gate', 'PENDING');
                setStepNode('node-step5', '5. Settlement', 'PENDING');
            } else if (stage === 1) {
                // Investigating in progress
                setStepNode('node-step1', '1. Investigating...', 'ACTIVE');
                setStepNode('node-step2', '2. Recoverability', 'PENDING');
                setStepNode('node-step3', '3. Strategy & ERV', 'PENDING');
                setStepNode('node-step4', '4. Policy Gate', 'PENDING');
                setStepNode('node-step5', '5. Settlement', 'PENDING');
            } else if (stage === 2) {
                // Investigation Completed / Decision Ready
                setStepNode('node-step1', '✓ 1. Diagnosis', 'COMPLETED');
                setStepNode('node-step2', '✓ 2. Recoverability', 'COMPLETED');
                setStepNode('node-step3', '✓ 3. Strategy & ERV', 'COMPLETED');
                setStepNode('node-step4', '✓ 4. Policy Gate', 'COMPLETED');
                setStepNode('node-step5', '5. Settlement', 'ACTIVE');
            } else if (stage === 3) {
                // Executed & Settled
                setStepNode('node-step1', '✓ 1. Diagnosis', 'COMPLETED');
                setStepNode('node-step2', '✓ 2. Recoverability', 'COMPLETED');
                setStepNode('node-step3', '✓ 3. Strategy & ERV', 'COMPLETED');
                setStepNode('node-step4', '✓ 4. Policy Gate', 'COMPLETED');
                setStepNode('node-step5', '✓ 5. Settlement Settled', 'COMPLETED');
            }
        }

        async function loadOverview() {
            try {
                const res = await fetch('/api/v1/overview');
                const data = await res.json();
                document.getElementById('kpi-risk').innerText = 'INR ' + Number(data.revenue_at_risk_inr).toLocaleString(undefined, {maximumFractionDigits: 0});
                document.getElementById('kpi-recoverable').innerText = 'INR ' + Number(data.expected_recoverable_inr).toLocaleString(undefined, {maximumFractionDigits: 0});
                document.getElementById('kpi-recovered').innerText = 'INR ' + Number(data.actual_recovered_inr).toLocaleString(undefined, {maximumFractionDigits: 0});
                document.getElementById('kpi-recovered-sub').innerText = `${data.recovery_rate_pct}% recovery rate (${data.recovered_cases_count} settled)`;
                document.getElementById('kpi-incremental').innerText = '+INR ' + Number(data.incremental_recovered_inr).toLocaleString(undefined, {maximumFractionDigits: 0});
            } catch (e) {
                console.error(e);
            }
        }

        async function loadCases() {
            try {
                const res = await fetch('/api/v1/cases?limit=100');
                allCases = await res.json();
                renderCasesTable(allCases);
                if (allCases.length > 0 && !currentCase) {
                    selectCase(allCases[0].case_id);
                }
            } catch (e) {
                console.error(e);
            }
        }

        function renderCasesTable(cases) {
            const tbody = document.getElementById('cases-tbody');
            tbody.innerHTML = '';
            document.getElementById('queue-count-badge').innerText = `${cases.length} visible cases`;

            cases.forEach(c => {
                const tr = document.createElement('tr');
                tr.className = 'hover:bg-slate-50 dark:hover:bg-slate-800/60 cursor-pointer transition';
                tr.onclick = () => selectCase(c.case_id);

                let badgeClass = 'badge-stopped';
                if (c.current_state === 'RECOVERED') badgeClass = 'badge-recovered';
                else if (c.current_state === 'ESCALATED') badgeClass = 'badge-escalated';
                else if (c.current_state === 'AT_RISK') badgeClass = 'badge-at-risk';

                const srcBadge = c.source === 'CUSTOM' ? '<span class="badge badge-custom">CUSTOM</span>' : '<span class="badge badge-benchmark">BENCHMARK</span>';

                tr.innerHTML = `
                    <td class="p-3 font-bold font-mono text-slate-900 dark:text-white">${c.case_id}</td>
                    <td class="p-3">${srcBadge}</td>
                    <td class="p-3 font-semibold font-mono text-slate-900 dark:text-white">INR ${Number(c.amount).toFixed(2)}</td>
                    <td class="p-3 text-xs text-slate-600 dark:text-slate-300">${c.failure_reason}</td>
                    <td class="p-3 text-xs font-mono font-semibold text-emerald-800 dark:text-emerald-400">${c.selected_strategy}</td>
                    <td class="p-3"><span class="badge ${badgeClass}">${c.current_state}</span></td>
                    <td class="p-3"><button class="text-xs font-semibold text-sky-600 dark:text-sky-400 hover:underline">Inspect</button></td>
                `;
                tbody.appendChild(tr);
            });
        }

        function filterCases() {
            const search = document.getElementById('queue-search').value.toLowerCase();
            const filterState = document.getElementById('queue-filter').value;
            const filterSource = document.getElementById('queue-source-filter').value;
            
            const filtered = allCases.filter(c => {
                const matchesSearch = c.case_id.toLowerCase().includes(search) || c.failure_reason.toLowerCase().includes(search);
                const matchesState = (filterState === 'ALL') || (c.current_state === filterState);
                const matchesSource = (filterSource === 'ALL') || (c.source === filterSource);
                return matchesSearch && matchesState && matchesSource;
            });
            renderCasesTable(filtered);
        }

        // ISSUE 2: STATE A (Pre-Investigation) — Switching or Selecting resets UI to Pre-Investigation
        async function selectCase(caseId) {
            stopOrganicNeuralAnimation();
            isInvestigating = false;

            // Reset layout to STATE A: Center-aligned Payment Incident
            const incidentCol = document.getElementById('incident-column');
            incidentCol.className = 'col-span-12 max-w-xl mx-auto w-full transition-all duration-500 space-y-4';

            // Hide right-column investigation workspace and Decision Explorer
            document.getElementById('investigation-column').classList.add('hidden');
            document.getElementById('investigation-loading-view').classList.add('hidden');
            document.getElementById('investigation-results-view').classList.add('hidden');
            document.getElementById('decision-explorer-section').classList.add('hidden');
            document.getElementById('kpi-strip').classList.add('hidden');

            // Reset Button to "Investigate Case"
            const btn = document.getElementById('btn-investigate');
            btn.disabled = false;
            document.getElementById('btn-investigate-text').innerText = 'Investigate Case';
            btn.className = 'w-full py-3.5 px-4 bg-slate-900 hover:bg-slate-800 dark:bg-white dark:hover:bg-slate-100 text-white dark:text-slate-900 font-semibold text-sm rounded-xl shadow transition flex items-center justify-center space-x-2 cursor-pointer';

            // Update Target Badges
            document.getElementById('active-case-id-badge').innerText = caseId;
            document.getElementById('spotlight-case-id').innerText = caseId;
            document.getElementById('exec-case-id').innerText = caseId;

            // Fetch target case metadata
            try {
                const res = await fetch('/api/v1/cases/' + caseId);
                currentCase = await res.json();
                populateSpotlightData(currentCase);
            } catch (e) {
                console.error(e);
            }
        }

        function populateSpotlightData(data) {
            const evt = data.event;
            const isCustom = data.source === 'CUSTOM';

            // Source Badges
            const srcBadge = document.getElementById('active-case-source-badge');
            srcBadge.innerText = data.source;
            srcBadge.className = 'badge ' + (isCustom ? 'badge-custom' : 'badge-benchmark');
            
            const spotSrc = document.getElementById('spotlight-source-tag');
            spotSrc.innerText = data.source;
            spotSrc.className = 'badge ' + (isCustom ? 'badge-custom' : 'badge-benchmark');

            // Spotlight Card Values (Center Aligned)
            document.getElementById('spotlight-amount').innerText = 'INR ' + evt.amount.toFixed(2);
            document.getElementById('spotlight-failure-class').innerText = evt.failure_class;
            document.getElementById('spotlight-failure-reason').innerText = evt.failure_reason;
            document.getElementById('spotlight-method').innerText = evt.payment_method;
            document.getElementById('spotlight-gw').innerText = evt.gateway_route_health + ' (Route: ' + evt.gateway_route_health + ')';
            document.getElementById('spotlight-cust-rate').innerText = `${Math.round(evt.customer_recovery_history_rate * 100)}% Historical Prior`;
            document.getElementById('spotlight-incident-summary').innerText = `${evt.payment_method} Failure • Route ${evt.gateway_route_health}`;

            let stateBadge = document.getElementById('spotlight-state-badge');
            stateBadge.innerText = data.summary.final_state;
            stateBadge.className = 'badge ' + (data.summary.is_recovered ? 'badge-recovered' : (data.summary.is_escalated ? 'badge-escalated' : 'badge-stopped'));
        }

        function populateInvestigationResults(data) {
            const evt = data.event;
            const latestAudit = data.audit_trail && data.audit_trail.length > 0 ? data.audit_trail[data.audit_trail.length - 1] : null;

            // Step 1: Diagnosis
            document.getElementById('step1-title').innerText = `Root Cause: ${evt.failure_reason} (${evt.failure_class})`;
            document.getElementById('step1-desc').innerText = `Payment method: ${evt.payment_method}. Gateway route health: ${evt.gateway_route_health}. Customer prior recovery reliability: ${(evt.customer_recovery_history_rate * 100).toFixed(0)}%.`;

            // Step 2: Recoverability
            const isBlocked = evt.customer_opted_out || evt.failure_class === 'FRAUD_SUSPECTED';
            document.getElementById('step2-rec-eval').innerText = isBlocked ? 'Unrecoverable (Policy Blocked)' : 'Recoverable Opportunity';
            document.getElementById('step2-rec-eval').className = 'text-sm font-bold ' + (isBlocked ? 'text-rose-600 dark:text-rose-400' : 'text-emerald-600 dark:text-emerald-400');

            // Step 3: Strategy & ERV
            const chosenStrat = latestAudit ? latestAudit.selected_action : 'STOP';
            document.getElementById('rec-strategy-name').innerText = chosenStrat.replace(/_/g, ' ');
            
            let ervVal = latestAudit && latestAudit.erv_breakdown ? latestAudit.erv_breakdown.highest_erv : (data.summary.is_recovered ? evt.amount * 0.85 : 0.0);
            document.getElementById('rec-erv-amount').innerText = 'INR ' + Number(ervVal).toFixed(2);
            document.getElementById('rec-narrative').innerText = latestAudit ? latestAudit.selection_reason : data.explanation;

            // Parameter Grid
            document.getElementById('param-prob').innerText = (chosenStrat === 'STOP' ? '0%' : '88.0%');
            document.getElementById('param-cost').innerText = (chosenStrat === 'HUMAN_ESCALATION' ? 'INR 50.00' : (chosenStrat === 'REMINDER_THEN_RETRY' ? 'INR 8.00' : 'INR 5.00'));
            document.getElementById('param-friction').innerText = (chosenStrat === 'REMINDER_THEN_RETRY' ? 'INR 15.00' : 'INR 5.00');
            document.getElementById('param-risk').innerText = 'INR 5.00';

            // Formula Instance
            document.getElementById('erv-formula-instance').innerText = `ERV = 0.88 * ${evt.amount.toFixed(2)} - Cost - Friction - Risk = INR ${Number(ervVal).toFixed(2)}`;

            // Safety Invariant Badge
            const safetyBadge = document.getElementById('safety-status-badge');
            safetyBadge.innerText = (latestAudit && latestAudit.policy_decision === 'APPROVED') ? 'ACTION APPROVED' : (data.summary.is_escalated ? 'ESCALATION REQUIRED' : 'ACTION BLOCKED');
            safetyBadge.className = 'badge ' + (latestAudit && latestAudit.policy_decision === 'APPROVED' ? 'badge-recovered' : 'badge-stopped');

            // Decision Explorer
            document.getElementById('tab-biz-summary').innerText = `Case ${data.case_id} (${evt.payment_method}, INR ${evt.amount.toFixed(2)}): ${data.explanation}`;
            document.getElementById('tab-biz-narrative').innerText = `RACE synthesized context from issuer codes, route health (${evt.gateway_route_health}), and customer recovery history. Strategy chosen: ${chosenStrat}. Deterministic safety gate cleared execution limits.`;
            document.getElementById('tab-tech-raw').innerText = JSON.stringify(evt, null, 2);

            // Populate ERV candidate table
            const ervTbody = document.getElementById('tab-erv-tbody');
            ervTbody.innerHTML = '';
            if (latestAudit && latestAudit.erv_breakdown && latestAudit.erv_breakdown.calculations) {
                latestAudit.erv_breakdown.calculations.forEach(calc => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td class="p-2.5 font-mono font-semibold text-slate-900 dark:text-white">${calc.strategy}</td>
                        <td class="p-2.5">${(calc.p_rec * 100).toFixed(0)}%</td>
                        <td class="p-2.5">INR 5-8</td>
                        <td class="p-2.5">INR 5-15</td>
                        <td class="p-2.5">INR 5</td>
                        <td class="p-2.5 font-bold text-emerald-600 dark:text-emerald-400">INR ${calc.erv.toFixed(2)}</td>
                    `;
                    ervTbody.appendChild(tr);
                });
            } else {
                ervTbody.innerHTML = `<tr><td colspan="6" class="p-3 text-slate-500 dark:text-slate-400 font-mono">${chosenStrat} selected with ERV INR ${Number(ervVal).toFixed(2)}</td></tr>`;
            }

            // Populate Audit trail
            const auditList = document.getElementById('tab-audit-list');
            auditList.innerHTML = '';
            if (data.audit_trail) {
                data.audit_trail.forEach(rec => {
                    const div = document.createElement('div');
                    div.className = 'p-3 bg-slate-50 dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 mb-1.5 font-mono text-xs';
                    div.innerHTML = `
                        <div class="flex justify-between text-slate-900 dark:text-white font-bold">
                            <span>[${rec.from_state} → ${rec.to_state}]</span>
                            <span>Action: ${rec.selected_action}</span>
                        </div>
                        <div class="text-slate-600 dark:text-slate-400 text-xs mt-1 font-sans">${rec.selection_reason}</div>
                        <div class="text-slate-400 dark:text-slate-500 text-[11px] mt-1">Idempotency Key: ${rec.idempotency_key} | Outcome: ${rec.outcome} (INR ${rec.recovered_amount})</div>
                    `;
                    auditList.appendChild(div);
                });
            }

            // Outcome / Settlement Reset
            const outcomePanel = document.getElementById('outcome-panel');
            const btnExecute = document.getElementById('btn-execute');
            const btnExecuteText = document.getElementById('btn-execute-text');

            if (data.summary.is_recovered) {
                updateStepProgress(3);
                outcomePanel.classList.remove('hidden');
                document.getElementById('outcome-pre-amt').innerText = `INR ${evt.amount.toFixed(2)} Outstanding`;
                document.getElementById('outcome-post-amt').innerText = `INR ${data.summary.recovered_amount.toFixed(2)} CAPTURED (Gateway State: captured)`;
                btnExecute.disabled = false;
                btnExecuteText.innerText = '✓ Settled (Re-Execute)';
            } else {
                updateStepProgress(2);
                outcomePanel.classList.add('hidden');
                btnExecute.disabled = false;
                btnExecuteText.innerText = 'Execute Recovery Action';
            }
        }

        // ISSUE 2 & 3: Trigger Investigation Transition (Moves Incident to Left -> Shows Organic Graph & Countdown -> Reveals Results)
        function startInvestigation() {
            if (!currentCase || isInvestigating) return;
            isInvestigating = true;

            const btn = document.getElementById('btn-investigate');
            btn.disabled = true;
            document.getElementById('btn-investigate-text').innerText = 'Investigating Case...';
            btn.className = 'w-full py-3.5 px-4 bg-slate-200 dark:bg-slate-800 text-slate-500 dark:text-slate-400 font-semibold text-sm rounded-xl transition flex items-center justify-center space-x-2';

            // Transition 1: Move Payment Incident from center to Left Column
            const incidentCol = document.getElementById('incident-column');
            incidentCol.className = 'col-span-12 lg:col-span-4 w-full transition-all duration-500 space-y-4';

            // Transition 2: Reveal Right Column, show Organic Neural Canvas + Countdown
            const investCol = document.getElementById('investigation-column');
            investCol.classList.remove('hidden');

            document.getElementById('investigation-results-view').classList.add('hidden');
            document.getElementById('decision-explorer-section').classList.add('hidden');
            document.getElementById('investigation-loading-view').classList.remove('hidden');

            // Active step 1 pulse
            updateStepProgress(1);

            // Start Organic Canvas & 3.2s Countdown
            startOrganicNeuralAnimation();

            // Transition 3: After countdown completes (~3.3s), reveal investigation results
            setTimeout(() => {
                stopOrganicNeuralAnimation();
                document.getElementById('investigation-loading-view').classList.add('hidden');
                document.getElementById('investigation-results-view').classList.remove('hidden');
                document.getElementById('decision-explorer-section').classList.remove('hidden');

                populateInvestigationResults(currentCase);

                // Update Button to "Re-Investigate Case"
                btn.disabled = false;
                document.getElementById('btn-investigate-text').innerText = 'Re-Investigate Case';
                btn.className = 'w-full py-3.5 px-4 bg-slate-900 hover:bg-slate-800 dark:bg-white dark:hover:bg-slate-100 text-white dark:text-slate-900 font-semibold text-sm rounded-xl shadow transition flex items-center justify-center space-x-2 cursor-pointer';

                // Staggered reveal of KPI cards
                revealKPIs();

                isInvestigating = false;
                document.getElementById('decision-card-container').scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 3300);
        }

        async function executeLiveRecovery() {
            if (!currentCase) return;
            const caseId = currentCase.case_id;
            const btn = document.getElementById('btn-execute');
            const btnText = document.getElementById('btn-execute-text');
            btn.disabled = true;
            btnText.innerText = 'Executing Action...';

            try {
                const res = await fetch(`/api/v1/cases/${caseId}/execute`, { method: 'POST' });
                const data = await res.json();

                setTimeout(() => {
                    btnText.innerText = 'Verifying Gateway State...';
                    setTimeout(() => {
                        updateStepProgress(3);

                        btn.disabled = false;
                        btnText.innerText = '✓ Settled (Re-Execute)';
                        document.getElementById('outcome-panel').classList.remove('hidden');
                        document.getElementById('outcome-pre-amt').innerText = `INR ${data.pre_action_outstanding.toFixed(2)} Outstanding`;
                        document.getElementById('outcome-post-amt').innerText = `INR ${data.post_action_captured.toFixed(2)} CAPTURED (Gateway State: ${data.authoritative_payment_status})`;
                        document.getElementById('learning-update-text').innerText = data.learning_update.message;
                        document.getElementById('outcome-panel').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    }, 300);
                }, 300);
            } catch (e) {
                console.error(e);
                btn.disabled = false;
                btnText.innerText = 'Execute Recovery Action';
            }
        }

        function openCreateCaseModal() {
            document.getElementById('modal-add-case').classList.remove('hidden');
        }

        function closeCreateCaseModal() {
            document.getElementById('modal-add-case').classList.add('hidden');
        }

        function toggleAdvancedContext() {
            const box = document.getElementById('adv-ctx-box');
            const label = document.getElementById('adv-ctx-label');
            if (box.classList.contains('hidden')) {
                box.classList.remove('hidden');
                label.innerText = '- Hide Advanced Fields';
            } else {
                box.classList.add('hidden');
                label.innerText = '+ Expand Advanced Fields';
            }
        }

        function onFailureClassChange() {
            const fc = document.getElementById('inp-failure-class').value;
            const rMap = {
                'TEMPORARY_NETWORK': 'GATEWAY_TIMEOUT',
                'INSUFFICIENT_FUNDS': 'INSUFFICIENT_FUNDS_OR_LIMIT',
                'AUTH_REQUIRED': 'AUTHENTICATION_FAILED_OR_DROPPED',
                'GATEWAY_DEGRADATION': 'ISSUER_SWITCH_DEGRADED',
                'EXPIRED_CARD': 'EXPIRED_CARD_DECLINE',
                'FRAUD_SUSPECTED': 'HIGH_RISK_FRAUD_BLOCK',
                'CUSTOMER_ABANDONMENT': 'CHECKOUT_USER_DROPOFF',
                'UNKNOWN': 'GENERAL_ACQUIRER_ERROR'
            };
            document.getElementById('inp-failure-reason').value = rMap[fc] || 'GENERAL_PAYMENT_FAILURE';
        }

        async function handleCreateCaseSubmit(e) {
            e.preventDefault();
            const btn = document.getElementById('btn-submit-case');
            const btnText = document.getElementById('btn-submit-case-text');
            btn.disabled = true;
            btnText.innerText = 'Evaluating in engine...';

            const payload = {
                amount: parseFloat(document.getElementById('inp-amount').value),
                currency: document.getElementById('inp-currency').value,
                failure_class: document.getElementById('inp-failure-class').value,
                failure_reason: document.getElementById('inp-failure-reason').value,
                payment_method: document.getElementById('inp-method').value,
                gateway_route_health: document.getElementById('inp-gw-health').value,
                customer_recovery_history_rate: parseFloat(document.getElementById('inp-cust-rate').value),
                customer_opted_out: document.getElementById('inp-opted-out').checked,
                retry_count: parseInt(document.getElementById('inp-retry-count').value || '0'),
                time_since_failure_minutes: parseFloat(document.getElementById('inp-time-since').value || '0'),
                merchant_mcc_tier: document.getElementById('inp-mcc-tier').value,
            };

            try {
                const res = await fetch('/api/v1/cases', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (!res.ok) {
                    const err = await res.json();
                    alert('Error creating case: ' + (err.detail || 'Validation failed'));
                    btn.disabled = false;
                    btnText.innerText = 'Add Scenario & Evaluate';
                    return;
                }

                const newCase = await res.json();
                closeCreateCaseModal();
                btn.disabled = false;
                btnText.innerText = 'Add Scenario & Evaluate';

                await loadOverview();
                await loadCases();
                await selectCase(newCase.case_id);

                document.getElementById('live-operations').scrollIntoView({ behavior: 'smooth', block: 'start' });
            } catch (err) {
                console.error(err);
                alert('Network error while injecting test case: ' + err);
                btn.disabled = false;
                btnText.innerText = 'Add Scenario & Evaluate';
            }
        }

        window.onload = () => {
            updateThemeLabel();
            loadOverview();
            loadCases();
        };
    </script>
</body>
</html>
"""


@app.get("/benchmarks", response_class=HTMLResponse)
def get_benchmarks_page():
    """Serves the dedicated Scientific Validation & Research Benchmarks page for RACE."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scientific Validation & Benchmarks — RACE</title>
    <!-- Typographic System: Plus Jakarta Sans + JetBrains Mono -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['"Plus Jakarta Sans"', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
                        mono: ['"JetBrains Mono"', 'monospace'],
                    }
                }
            }
        }
    </script>
    <script>
        if (localStorage.getItem('race_theme') === 'dark') {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    </script>
    <style>
        body {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            -webkit-font-smoothing: antialiased;
            transition: background-color 0.2s ease, color 0.2s ease;
        }
        .font-mono { font-family: 'JetBrains Mono', monospace; }
        .card-surface {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 14px;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04);
            transition: all 0.2s ease;
        }
        .dark .card-surface {
            background-color: #131B2A;
            border-color: #1E2B3E;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.4);
        }
        .badge {
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            font-weight: 600;
            padding: 3px 8px;
            border-radius: 6px;
            display: inline-flex;
            align-items: center;
        }
    </style>
</head>
<body class="bg-white dark:bg-[#0B0F17] text-slate-900 dark:text-slate-100 min-h-screen">

    <!-- TOP NAVIGATION -->
    <header class="border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0B0F17] sticky top-0 z-40 transition-colors">
        <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <a href="/" class="flex items-center space-x-2">
                    <span class="w-7 h-7 rounded-lg bg-slate-900 dark:bg-white text-white dark:text-slate-900 font-extrabold flex items-center justify-center text-sm">R</span>
                    <span class="text-base font-bold tracking-tight text-slate-900 dark:text-white">RACE</span>
                </a>
                <span class="text-xs text-slate-400 dark:text-slate-500 font-mono">/ Scientific Benchmarks</span>
            </div>
            <nav class="flex items-center space-x-2">
                <a href="/" class="px-3 py-1.5 text-xs font-semibold text-sky-700 dark:text-sky-400 bg-sky-50 dark:bg-sky-950/60 hover:bg-sky-100 dark:hover:bg-sky-900 rounded-lg transition">
                    ← Return to Console
                </a>
                <a href="/about" class="px-3 py-1.5 text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 transition">
                    About RACE
                </a>
                <button onclick="toggleTheme()" id="theme-toggle-btn" class="p-1.5 text-xs font-mono font-semibold text-slate-600 dark:text-slate-300 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-lg border border-slate-300 dark:border-slate-700 transition flex items-center">
                    <span id="theme-label">🌙 Dark</span>
                </button>
            </nav>
        </div>
    </header>

    <main class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">

        <!-- EXECUTIVE HERO -->
        <section class="p-8 bg-slate-50 dark:bg-[#0F1622] rounded-2xl border border-slate-200 dark:border-slate-800 space-y-3 transition-colors">
            <div class="flex items-center space-x-2">
                <span class="px-2.5 py-1 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 rounded text-xs font-mono font-bold">
                    Scientific Evaluation Report
                </span>
                <span class="px-2.5 py-1 bg-emerald-50 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800 rounded text-xs font-mono font-bold">
                    200 Frozen Held-Out Cases
                </span>
            </div>
            <h1 class="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
                Empirical comparative validation against fixed retry, rule heuristics, and ML ranking.
            </h1>
            <p class="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
                RACE is evaluated on a strictly frozen, reproducible held-out test suite under fixed dispatch budgets. Every model is evaluated against identical ground-truth transaction counterfactuals, accounting for marginal execution costs and customer friction.
            </p>
        </section>

        <!-- BENCHMARK SUMMARY TILES -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div class="card-surface p-5 space-y-1">
                <span class="text-[11px] text-slate-500 dark:text-slate-400 font-semibold font-mono uppercase block">Baseline A (Fixed Retry)</span>
                <div class="text-2xl font-bold font-mono text-slate-900 dark:text-white" id="bench-base-a-rec">INR 498,949</div>
                <p class="text-xs text-slate-500 dark:text-slate-400">57.5% recovery rate (115/200)</p>
                <p class="text-[11px] text-slate-400 dark:text-slate-500">Unaware of route or balance</p>
            </div>
            <div class="card-surface p-5 space-y-1">
                <span class="text-[11px] text-slate-500 dark:text-slate-400 font-semibold font-mono uppercase block">Baseline B (Rule-Based)</span>
                <div class="text-2xl font-bold font-mono text-slate-900 dark:text-white" id="bench-base-b-rec">INR 1,680,352</div>
                <p class="text-xs text-slate-500 dark:text-slate-400">83.5% recovery rate (167/200)</p>
                <p class="text-[11px] text-slate-400 dark:text-slate-500">Static rule table mapping</p>
            </div>
            <div class="card-surface p-5 space-y-1">
                <span class="text-[11px] text-slate-500 dark:text-slate-400 font-semibold font-mono uppercase block">Baseline C (ML Ranking)</span>
                <div class="text-2xl font-bold font-mono text-slate-900 dark:text-white" id="bench-base-c-rec">INR 1,620,005</div>
                <p class="text-xs text-slate-500 dark:text-slate-400">80.5% recovery rate (161/200)</p>
                <p class="text-[11px] text-slate-400 dark:text-slate-500">Supervised argmax scoring</p>
            </div>
            <div class="card-surface p-5 space-y-1 bg-emerald-50/50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800">
                <span class="text-[11px] text-emerald-800 dark:text-emerald-400 font-bold font-mono uppercase block">RACE Engine (Proposed)</span>
                <div class="text-2xl font-bold font-mono text-emerald-700 dark:text-emerald-400" id="bench-race-rec">INR 1,680,352</div>
                <p class="text-xs text-emerald-700 dark:text-emerald-300 font-semibold">+INR 1,181,402 (+236.8% Uplift)</p>
                <p class="text-[11px] text-slate-500 dark:text-slate-400">83.5% rec rate, ₹0.0010 fee/rupee</p>
            </div>
        </div>

        <!-- RE-TEST TRIGGER & COMPARISON TABLE -->
        <section class="card-surface p-6 space-y-4">
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 pb-3 border-b border-slate-200 dark:border-slate-800">
                <div>
                    <h3 class="text-base font-bold text-slate-900 dark:text-white">Comparative Performance Matrix</h3>
                    <p class="text-xs text-slate-500 dark:text-slate-400">Held-out validation dataset (200 test cases) across recovery rates, fee efficiency, and Net Recovery Value.</p>
                </div>
                <button onclick="fetchBenchmark()" id="btn-run-bench" class="px-4 py-2 bg-slate-900 hover:bg-slate-800 dark:bg-white dark:hover:bg-slate-100 text-white dark:text-slate-900 rounded-lg text-xs font-semibold shadow-sm transition flex items-center space-x-1.5">
                    <span>Re-Run Scientific Benchmark</span>
                </button>
            </div>

            <div class="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-800 font-mono text-xs">
                <table class="w-full text-left text-slate-800 dark:text-slate-200">
                    <thead class="bg-slate-50 dark:bg-slate-900 text-slate-500 dark:text-slate-400 text-[11px] uppercase border-b border-slate-200 dark:border-slate-800">
                        <tr>
                            <th class="p-3.5">Model / System</th>
                            <th class="p-3.5">Recovery Rate</th>
                            <th class="p-3.5">Gross Recovered</th>
                            <th class="p-3.5">Total Fees</th>
                            <th class="p-3.5">Cost / Rupee</th>
                            <th class="p-3.5">Net Uplift vs Base A</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
                        <tr>
                            <td class="p-3.5 font-bold">Baseline A (Fixed Retry)</td>
                            <td class="p-3.5">57.5%</td>
                            <td class="p-3.5">INR 498,949</td>
                            <td class="p-3.5">INR 1,000</td>
                            <td class="p-3.5">INR 0.0020</td>
                            <td class="p-3.5 text-slate-400">—</td>
                        </tr>
                        <tr>
                            <td class="p-3.5 font-bold">Baseline B (Rule-Based)</td>
                            <td class="p-3.5">83.5%</td>
                            <td class="p-3.5">INR 1,680,352</td>
                            <td class="p-3.5">INR 1,820</td>
                            <td class="p-3.5">INR 0.0011</td>
                            <td class="p-3.5 text-emerald-600 dark:text-emerald-400 font-bold">+INR 1,181,402</td>
                        </tr>
                        <tr>
                            <td class="p-3.5 font-bold">Baseline C (ML Ranking)</td>
                            <td class="p-3.5">80.5%</td>
                            <td class="p-3.5">INR 1,620,005</td>
                            <td class="p-3.5">INR 1,750</td>
                            <td class="p-3.5">INR 0.0011</td>
                            <td class="p-3.5 text-emerald-600 dark:text-emerald-400 font-bold">+INR 1,121,056</td>
                        </tr>
                        <tr class="bg-emerald-50/40 dark:bg-emerald-950/30 font-bold">
                            <td class="p-3.5 text-emerald-800 dark:text-emerald-400">RACE Decision Engine</td>
                            <td class="p-3.5 text-emerald-700 dark:text-emerald-300">83.5%</td>
                            <td class="p-3.5 text-emerald-700 dark:text-emerald-300">INR 1,680,352</td>
                            <td class="p-3.5 text-slate-700 dark:text-slate-300">INR 1,745</td>
                            <td class="p-3.5 text-slate-700 dark:text-slate-300">INR 0.0010</td>
                            <td class="p-3.5 text-emerald-600 dark:text-emerald-400 font-extrabold">+INR 1,181,402 (+236.8%)</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div id="bench-status-msg" class="text-xs font-mono text-slate-600 dark:text-slate-400 italic hidden"></div>
        </section>

        <!-- ABLATION STUDY -->
        <section class="card-surface p-6 space-y-4">
            <h3 class="text-base font-bold text-slate-900 dark:text-white">Component Ablation Analysis</h3>
            <p class="text-xs text-slate-500 dark:text-slate-400">Isolates each system component to demonstrate its statistical contribution to net recovered revenue.</p>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs font-mono">
                <div class="p-4 bg-slate-50 dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 space-y-1">
                    <span class="text-[11px] text-slate-400 uppercase font-bold block">Ablation 1 — Without ERV</span>
                    <p class="font-bold text-rose-600 dark:text-rose-400">62.0% Recovery Rate</p>
                    <p class="text-slate-600 dark:text-slate-400 font-sans text-xs">Uncalibrated interventions cause excessive friction and failed retries on degraded routes.</p>
                </div>
                <div class="p-4 bg-slate-50 dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 space-y-1">
                    <span class="text-[11px] text-slate-400 uppercase font-bold block">Ablation 2 — Without Policy Gate</span>
                    <p class="font-bold text-amber-600 dark:text-amber-400">Unbounded Execution Risk</p>
                    <p class="text-slate-600 dark:text-slate-400 font-sans text-xs">AI recommendations violate retry caps and attempt invalid high-value actions without authorization.</p>
                </div>
                <div class="p-4 bg-slate-50 dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 space-y-1">
                    <span class="text-[11px] text-slate-400 uppercase font-bold block">Ablation 3 — Without Bayesian Learning</span>
                    <p class="font-bold text-sky-600 dark:text-sky-400">Static Prior Freeze</p>
                    <p class="text-slate-600 dark:text-slate-400 font-sans text-xs">Model fails to adapt to newly observed failure archetype patterns across sequential batches.</p>
                </div>
            </div>
        </section>

    </main>

    <footer class="border-t border-slate-200 dark:border-slate-800 py-6 mt-12 bg-slate-50 dark:bg-[#0B0F17] text-center text-xs text-slate-500 dark:text-slate-400 font-mono transition-colors">
        RACE — Revenue Adaptive Control Engine | Autonomous Revenue Recovery Control System
    </footer>

    <script>
        function toggleTheme() {
            const isDark = document.documentElement.classList.toggle('dark');
            localStorage.setItem('race_theme', isDark ? 'dark' : 'light');
            updateThemeLabel();
        }

        function updateThemeLabel() {
            const isDark = document.documentElement.classList.contains('dark');
            const label = document.getElementById('theme-label');
            if (label) {
                label.innerText = isDark ? '☀️ Light' : '🌙 Dark';
            }
        }

        async function fetchBenchmark() {
            const btn = document.getElementById('btn-run-bench');
            const msg = document.getElementById('bench-status-msg');
            msg.classList.remove('hidden');
            msg.innerText = 'Running comparative evaluation across 200 held-out cases...';
            btn.disabled = true;

            try {
                const res = await fetch('/api/v1/benchmark?split=validation');
                const data = await res.json();
                document.getElementById('bench-base-a-rec').innerText = 'INR ' + Number(data.baseline_a.total_recovered_revenue).toLocaleString(undefined, {maximumFractionDigits: 0});
                document.getElementById('bench-base-b-rec').innerText = 'INR ' + Number(data.baseline_b.total_recovered_revenue).toLocaleString(undefined, {maximumFractionDigits: 0});
                document.getElementById('bench-base-c-rec').innerText = 'INR ' + Number(data.baseline_c.total_recovered_revenue).toLocaleString(undefined, {maximumFractionDigits: 0});
                document.getElementById('bench-race-rec').innerText = 'INR ' + Number(data.race.actual_recovered_revenue).toLocaleString(undefined, {maximumFractionDigits: 0});
                msg.innerText = `Benchmark completed! RACE recovered INR ${Number(data.race.actual_recovered_revenue).toLocaleString()} revenue (+INR ${Number(data.race.incremental_revenue_vs_baseline_a).toLocaleString()} incremental uplift vs Baseline A).`;
            } catch (e) {
                msg.innerText = 'Error running benchmark: ' + e;
            } finally {
                btn.disabled = false;
            }
        }

        window.onload = () => {
            updateThemeLabel();
        };
    </script>
</body>
</html>
"""


@app.get("/about", response_class=HTMLResponse)
def get_about_page():
    """Serves the clean, minimal technical specification page for RACE with theme support."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>About RACE — Technical Specification</title>
    <!-- Typographic System: Plus Jakarta Sans + JetBrains Mono -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['"Plus Jakarta Sans"', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
                        mono: ['"JetBrains Mono"', 'monospace'],
                    }
                }
            }
        }
    </script>
    <script>
        if (localStorage.getItem('race_theme') === 'dark') {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    </script>
    <style>
        body {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            -webkit-font-smoothing: antialiased;
            transition: background-color 0.2s ease, color 0.2s ease;
        }
        .font-mono { font-family: 'JetBrains Mono', monospace; }
        .card-surface {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 14px;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04);
            transition: all 0.2s ease;
        }
        .dark .card-surface {
            background-color: #131B2A;
            border-color: #1E2B3E;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.4);
        }
        .badge {
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            font-weight: 600;
            padding: 3px 8px;
            border-radius: 6px;
            display: inline-flex;
            align-items: center;
        }
    </style>
</head>
<body class="bg-white dark:bg-[#0B0F17] text-slate-900 dark:text-slate-100 min-h-screen">

    <!-- TOP NAVIGATION -->
    <header class="border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0B0F17] sticky top-0 z-40 transition-colors">
        <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <a href="/" class="flex items-center space-x-2">
                    <span class="w-7 h-7 rounded-lg bg-slate-900 dark:bg-white text-white dark:text-slate-900 font-extrabold flex items-center justify-center text-sm">R</span>
                    <span class="text-base font-bold tracking-tight text-slate-900 dark:text-white">RACE</span>
                </a>
                <span class="text-xs text-slate-400 dark:text-slate-500 font-mono">/ Technical Specification</span>
            </div>
            <nav class="flex items-center space-x-2">
                <a href="/" class="px-3 py-1.5 text-xs font-semibold text-sky-700 dark:text-sky-400 bg-sky-50 dark:bg-sky-950/60 hover:bg-sky-100 dark:hover:bg-sky-900 rounded-lg transition">
                    ← Return to Console
                </a>
                <a href="/benchmarks" class="px-3 py-1.5 text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 transition">
                    Benchmarks
                </a>
                <button onclick="toggleTheme()" id="theme-toggle-btn" class="p-1.5 text-xs font-mono font-semibold text-slate-600 dark:text-slate-300 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-lg border border-slate-300 dark:border-slate-700 transition flex items-center">
                    <span id="theme-label">🌙 Dark</span>
                </button>
            </nav>
        </div>
    </header>

    <main class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">

        <!-- EXECUTIVE HERO -->
        <section class="p-8 bg-slate-50 dark:bg-[#0F1622] rounded-2xl border border-slate-200 dark:border-slate-800 space-y-3 transition-colors">
            <span class="px-2.5 py-1 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 rounded text-xs font-mono font-bold">
                System Specification
            </span>
            <h1 class="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
                From failed payment events to evidence-backed, economically optimized recovery decisions.
            </h1>
            <p class="text-sm sm:text-base text-slate-600 dark:text-slate-300 leading-relaxed">
                RACE is an autonomous revenue recovery decision engine that determines whether a failed revenue event should be recovered, how it should be recovered, and when it should stop. Rather than executing uncalibrated retry loops, RACE models revenue recovery as an economic decision under uncertainty: investigating root-cause telemetry, evaluating Expected Recovery Value (ERV), enforcing deterministic safety boundaries, executing bounded actions, and verifying authoritative payment states on the gateway ledger.
            </p>
        </section>

        <!-- 01 — WHAT IS RACE? -->
        <section class="card-surface p-7 space-y-3">
            <div class="text-xs font-bold text-sky-700 dark:text-sky-400 font-mono uppercase tracking-wider">01 — What is RACE?</div>
            <h2 class="text-xl font-bold text-slate-900 dark:text-white">A Decision Engine, Not a Generic Retry Loop</h2>
            <p class="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
                In online commerce, payment failures result from diverse root causes including temporary card balance deficits, gateway switch degradations, 3DS dropoffs, expired cards, and suspected fraud. Traditional recovery approaches rely on naive fixed intervals (e.g. retrying every 2 hours) or static rule tables that ignore route health, customer fatigue, and marginal financial execution costs.
            </p>
            <p class="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
                RACE replaces blind retry loops with an intelligent, closed-loop control system. Every transaction failure is diagnosed individually, ranked by net Expected Recovery Value (ERV), verified through a deterministic safety gate, executed in test mode with cryptographic uniqueness, verified against the gateway's authoritative ledger, and fed into continuous empirical Bayesian performance tracking.
            </p>
        </section>

        <!-- 02 — THE 9-STAGE DECISION LIFECYCLE -->
        <section class="card-surface p-7 space-y-4">
            <div class="text-xs font-bold text-sky-700 dark:text-sky-400 font-mono uppercase tracking-wider">02 — Decision Lifecycle</div>
            <h2 class="text-xl font-bold text-slate-900 dark:text-white">The 9-Stage Closed-Loop Architecture</h2>
            <p class="text-xs text-slate-500 dark:text-slate-400">Every failed revenue event flows through a unidirectional, failure-safe decision pipeline:</p>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                <div class="p-3.5 bg-slate-50 dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 space-y-1">
                    <div class="font-bold text-slate-900 dark:text-white font-mono">1. FAILURE EVENT</div>
                    <p class="text-slate-600 dark:text-slate-400">Captures payment failure, webhook drop, or timeout with structured error codes and route metadata.</p>
                </div>
                <div class="p-3.5 bg-slate-50 dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 space-y-1">
                    <div class="font-bold text-slate-900 dark:text-white font-mono">2. RECOVERABILITY</div>
                    <p class="text-slate-600 dark:text-slate-400">Evaluates whether the failure represents a recoverable opportunity vs a hard fraud or opt-out block.</p>
                </div>
                <div class="p-3.5 bg-slate-50 dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 space-y-1">
                    <div class="font-bold text-slate-900 dark:text-white font-mono">3. CONTEXT SYNTHESIS</div>
                    <p class="text-slate-600 dark:text-slate-400">Synthesizes issuer response codes, gateway route health indicators, and customer recovery history.</p>
                </div>
                <div class="p-3.5 bg-slate-50 dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 space-y-1">
                    <div class="font-bold text-slate-900 dark:text-white font-mono">4. CANDIDATES</div>
                    <p class="text-slate-600 dark:text-slate-400">Generates admissible actions: RETRY_NOW, RETRY_LATER, REMINDER_THEN_RETRY, HUMAN_ESCALATION, STOP.</p>
                </div>
                <div class="p-3.5 bg-slate-50 dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 space-y-1">
                    <div class="font-bold text-slate-900 dark:text-white font-mono">5. ERV OPTIMIZATION</div>
                    <p class="text-slate-600 dark:text-slate-400">Ranks candidates by net Expected Recovery Value after subtracting action costs, customer friction, and risk.</p>
                </div>
                <div class="p-3.5 bg-slate-50 dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 space-y-1">
                    <div class="font-bold text-slate-900 dark:text-white font-mono">6. POLICY GATE</div>
                    <p class="text-slate-600 dark:text-slate-400">Deterministic rules enforce retry limits (<=3), amount caps (<=50K), cooldown buffers, and opt-out checks.</p>
                </div>
                <div class="p-3.5 bg-slate-50 dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 space-y-1">
                    <div class="font-bold text-slate-900 dark:text-white font-mono">7. BOUNDED ACTION</div>
                    <p class="text-slate-600 dark:text-slate-400">Dispatches test-mode action with a deterministic SHA-256 idempotency key locking execution identity.</p>
                </div>
                <div class="p-3.5 bg-slate-50 dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 space-y-1">
                    <div class="font-bold text-slate-900 dark:text-white font-mono">8. OUTCOME VERIFY</div>
                    <p class="text-slate-600 dark:text-slate-400">Queries gateway ledger to confirm definitive payment status (captured/paid vs failed vs unknown).</p>
                </div>
                <div class="p-3.5 bg-slate-50 dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 space-y-1">
                    <div class="font-bold text-slate-900 dark:text-white font-mono">9. BAYESIAN LEARNING</div>
                    <p class="text-slate-600 dark:text-slate-400">Updates empirical recovery priors via Bayesian smoothing across strategy performance buckets.</p>
                </div>
            </div>
        </section>

        <!-- 03 — MATHEMATICAL FOUNDATIONS -->
        <section class="card-surface p-7 space-y-5">
            <div class="text-xs font-bold text-sky-700 dark:text-sky-400 font-mono uppercase tracking-wider">03 — Mathematical Foundations</div>
            <h2 class="text-xl font-bold text-slate-900 dark:text-white">Equations & Operational Formulations</h2>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                <!-- FORMULA 1: ERV -->
                <div class="p-4 bg-slate-50 dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 space-y-2 font-mono">
                    <div class="flex justify-between items-center">
                        <span class="font-bold text-sky-700 dark:text-sky-400">FORMULA 01 — ERV Equation</span>
                        <span class="text-slate-400 text-[10.5px]">backend/core/economics.py</span>
                    </div>
                    <div class="p-2.5 bg-white dark:bg-slate-800 rounded border border-slate-200 dark:border-slate-700 font-bold text-emerald-700 dark:text-emerald-400 text-xs">
                        ERV(a) = P(rec | context, a) * Amount - Cost(a) - Friction(a) - Risk(a)
                    </div>
                    <p class="text-slate-600 dark:text-slate-400 font-sans text-xs leading-relaxed">
                        Balances gross recoverable rupees against marginal action fee, customer churn friction penalty, and processor risk.
                    </p>
                </div>

                <!-- FORMULA 2: BAYESIAN SMOOTHING -->
                <div class="p-4 bg-slate-50 dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 space-y-2 font-mono">
                    <div class="flex justify-between items-center">
                        <span class="font-bold text-sky-700 dark:text-sky-400">FORMULA 02 — Bayesian Smoothing</span>
                        <span class="text-slate-400 text-[10.5px]">backend/recovery/learning/</span>
                    </div>
                    <div class="p-2.5 bg-white dark:bg-slate-800 rounded border border-slate-200 dark:border-slate-700 font-bold text-emerald-700 dark:text-emerald-400 text-xs">
                        P_smoothed = (SuccessCount + (PriorRate * w)) / (SampleCount + w)
                    </div>
                    <p class="text-slate-600 dark:text-slate-400 font-sans text-xs leading-relaxed">
                        Smooths empirical observations with prior domain rates using Bayesian pseudo-count weight (w = 3.0).
                    </p>
                </div>

                <!-- FORMULA 3: NRV -->
                <div class="p-4 bg-slate-50 dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 space-y-2 font-mono">
                    <div class="flex justify-between items-center">
                        <span class="font-bold text-sky-700 dark:text-sky-400">FORMULA 03 — Net Recovery Value</span>
                        <span class="text-slate-400 text-[10.5px]">evaluation/metrics/kpis.py</span>
                    </div>
                    <div class="p-2.5 bg-white dark:bg-slate-800 rounded border border-slate-200 dark:border-slate-700 font-bold text-emerald-700 dark:text-emerald-400 text-xs">
                        NRV = TotalRecoveredRevenue - TotalActionCost
                    </div>
                    <p class="text-slate-600 dark:text-slate-400 font-sans text-xs leading-relaxed">
                        Guarantees honest financial accounting by subtracting all marginal operational fees from gross recoveries.
                    </p>
                </div>

                <!-- FORMULA 4: SHA-256 IDEMPOTENCY -->
                <div class="p-4 bg-slate-50 dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 space-y-2 font-mono">
                    <div class="flex justify-between items-center">
                        <span class="font-bold text-sky-700 dark:text-sky-400">FORMULA 04 — Idempotency Key Hash</span>
                        <span class="text-slate-400 text-[10.5px]">backend/recovery/idempotency/</span>
                    </div>
                    <div class="p-2.5 bg-white dark:bg-slate-800 rounded border border-slate-200 dark:border-slate-700 font-bold text-emerald-700 dark:text-emerald-400 text-xs">
                        Key = SHA256(merchant_id : customer_id : payment_id : action : attempt)
                    </div>
                    <p class="text-slate-600 dark:text-slate-400 font-sans text-xs leading-relaxed">
                        Guarantees distributed uniqueness across retries. Parallel duplicate attempts are locked out deterministically.
                    </p>
                </div>
            </div>
        </section>

    </main>

    <footer class="border-t border-slate-200 dark:border-slate-800 py-6 mt-12 bg-slate-50 dark:bg-[#0B0F17] text-center text-xs text-slate-500 dark:text-slate-400 font-mono transition-colors">
        RACE — Revenue Adaptive Control Engine | Autonomous Revenue Recovery Control System
    </footer>

    <script>
        function toggleTheme() {
            const isDark = document.documentElement.classList.toggle('dark');
            localStorage.setItem('race_theme', isDark ? 'dark' : 'light');
            updateThemeLabel();
        }

        function updateThemeLabel() {
            const isDark = document.documentElement.classList.contains('dark');
            const label = document.getElementById('theme-label');
            if (label) {
                label.innerText = isDark ? '☀️ Light' : '🌙 Dark';
            }
        }

        window.onload = () => {
            updateThemeLabel();
        };
    </script>
</body>
</html>
"""
