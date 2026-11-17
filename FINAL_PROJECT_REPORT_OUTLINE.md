# InsightForge AI — Final Project Report Outline
## An Augmented Commercial Analytics Platform with Grounded AI Prompt Engineering

**Capstone Project Report Outline**  
**Course:** Third-Year Computer Science — Advanced Prompt Engineering & Applied AI Systems  
**Academic Year:** 2026–2027  

---

## Abstract

Generative Large Language Models (LLMs) have demonstrated remarkable capabilities in qualitative reasoning, narrative synthesis, and natural language communication. However, when deployed in commercial Business Intelligence (BI) and enterprise decision-making, unconstrained LLMs exhibit fatal failure modes: arithmetic hallucination, stochastic aggregation discrepancies, structural JSON invalidity, and susceptibility to indirect prompt injection. 

This project presents **InsightForge AI**, a mobile-first, multi-tenant B2B SaaS augmented commercial analytics platform designed to solve the arithmetic and structural reliability challenges of generative AI in commercial decision systems. We propose and evaluate the **Decoupled Deterministic-Generative Principle**: *Generative language models must never perform arithmetic calculations on commercial data; all mathematical aggregations must be computed deterministically and injected into structured prompt pipelines as immutable evidence bounds.*

We implement and evaluate:
1. A **three-stage prompt engineering chain** (Factual Summarization $\rightarrow$ Strategic Hypotheses $\rightarrow$ Structured Report) with Jinja2 versioning (v1 baseline vs. v2 evidence-grounded).
2. A **deterministic verification engine** auditing numerical citations within a 0.5% tolerance threshold and enforcing mandatory refusal (`"Insufficient data"`) for unrecorded causal drivers or profit margins.
3. A **supervised and unsupervised ML subsystem** combining XGBoost multi-step recursive sales forecasting with chronological holdout validation against a Seasonal Naive baseline, and Isolation Forest transaction outlier detection.
4. A **workspace-scoped hybrid RAG knowledge base** embedding enterprise contracts using dense 384-dimensional vectors with pre-embedding prompt injection sanitization.
5. A **controlled LangGraph business analysis agent** executing strictly vetted tools without arbitrary Python or SQL execution.
6. A **vector-rendered executive PDF reporting engine** compiling audit-grade multi-page briefs with embedded high-resolution figures.

Across controlled empirical evaluations on a benchmark wholesale dataset (5,015 transactions), Prompt v2 achieved **100.0% numerical accuracy** (vs. 33.3% for Prompt v1), **0 hallucinations**, **100.0% JSON schema conformance**, and a **90.0% anomaly detection recall**, demonstrating a reproducible blueprint for reliable AI-augmented analytics.

---

## Table of Contents

1. **Introduction and Problem Statement**
   - 1.1 Commercial Analytics Challenges in Wholesale Distribution and B2B Retail
   - 1.2 The Arithmetic Hallucination Dilemma in Generative AI
   - 1.3 Project Objectives and Academic Scope
   - 1.4 Primary Research Contributions

2. **Literature Review and Theoretical Foundations**
   - 2.1 Evolution of Business Intelligence and Augmented Analytics
   - 2.2 Mathematical Limitations and Tokenization Pitfalls in Transformer Models
   - 2.3 Prompt Engineering Methodologies: In-Context Learning, Chain-of-Thought, and Structured Output Enforcement
   - 2.4 Retrieval-Augmented Generation (RAG) and Indirect Prompt Injection Vulnerabilities
   - 2.5 Autonomous AI Agent Frameworks: ReAct, LangGraph, and Safety Boundary Enforcement

3. **System Architecture and Design Principles**
   - 3.1 High-Level Architecture: The Modular Monolith Paradigm
   - 3.2 Multi-Tenant Workspace Scoping and Tenant Isolation
   - 3.3 The Decoupled Deterministic-Generative Architecture
   - 3.4 Data Ingestion, Column Role Auto-Detection, and Quality Auditing Pipeline
   - 3.5 Deterministic Metric Aggregation Engine (Vectorized Pandas)

4. **Evidence-Grounded Prompt Engineering Engine**
   - 4.1 Three-Stage Chained Prompt Design
     - *Stage 1: Factual Summarization (`prompt1_factual_v2.jinja2`)*
     - *Stage 2: Strategic Insights & Hypotheses (`prompt2_insights_v2.jinja2`)*
     - *Stage 3: Executive Report Formatting (`prompt3_report_v2.jinja2`)*
   - 4.2 Architectural Comparison: Prompt v1 (Loose Markdown) vs. Prompt v2 (Structured Evidence)
   - 4.3 Deterministic Verification Engine: Metric ID Auditing, Tolerance Windows, and Auto-Repair
   - 4.4 Mandatory Refusal Architecture for Missing Data and Margin Protection

5. **Machine Learning Intelligence Subsystem**
   - 5.1 Time-Series Sales Forecasting: XGBoost Regressor with Chronological Holdout Validation
   - 5.2 Target Leakage Prevention: Forward-Shifted Lags and Rolling Windows
   - 5.3 Baseline Disciplines: Empirical Comparison against Seasonal Naive Lag-1 Persistence
   - 5.4 Transaction Anomaly Detection: Isolation Forest with SKU-Relative Deviation Metrics
   - 5.5 Commercial Disclosures: Mathematical Outlier Isolation vs. Confirmed Fraud

6. **Enterprise Knowledge Base & Hybrid RAG Retrieval**
   - 6.1 Unstructured Document Ingestion (PDF & TXT Extraction)
   - 6.2 Sliding-Window Chunking and Metadata Provenance Preservation
   - 6.3 Semantic Dense Embeddings (`all-MiniLM-L6-v2`) and Cosine Similarity Retrieval
   - 6.4 Security Guardrails: Pre-Embedding Prompt Injection Neutralization
   - 6.5 Prompt Grounding: Contextual Policy Citations without Numerical Drift

7. **Controlled Agentic AI Business Analyst**
   - 7.1 LangGraph Stateful Graph Topology (`classify_and_plan` $\rightarrow$ `validate_arguments` $\rightarrow$ `execute_tools` $\rightarrow$ `synthesize_response`)
   - 7.2 Approved Commercial Tool Suite (7 Vetted Operations)
   - 7.3 Boundary Enforcement: Elimination of Arbitrary Code/SQL Execution and Parameter Clamping
   - 7.4 Explainable Execution Traces and Interactive Multi-Modal Visualizations

8. **Boardroom Executive Reporting & Mobile-First Frontend**
   - 8.1 Vector-Rendered Multi-Page PDF Compiler (ReportLab & Matplotlib)
   - 8.2 Dynamic Page Numbering (`NumberedCanvas`) and Corporate Design System
   - 8.3 Mobile-First Responsive UI (React 18, TypeScript, Tailwind CSS, Recharts)
   - 8.4 Progressive Web App (PWA) Implementation and Service Worker Caching Topology

9. **Empirical Evaluation, Benchmarks, and Research Findings**
   - 9.1 Experimental Methodology and Benchmark Dataset Construction
   - 9.2 Prompt v1 vs. Prompt v2 Empirical Ablation Study
   - 9.3 Machine Learning Performance: Honest Outperformance Reporting and Limitations
   - 9.4 Anomaly Detection Recall on Controlled Synthetic Injections
   - 9.5 RAG Retrieval Precision, Latency, and Tenant Isolation Verification
   - 9.6 Agent Tool Routing Reliability and Injection Defense
   - 9.7 Human Usefulness Rubric Across 5 Commercial Dimensions

10. **Threat Model and Security Analysis**
    - 10.1 Multi-Tenant Cross-Workspace Data Leakage Protection
    - 10.2 Adversarial Prompt Injection and Goal Hijacking Mitigation
    - 10.3 Password Security: Direct Native Bcrypt with 72-Byte Truncation Boundaries
    - 10.4 Safe Demo Mode vs. Authenticated Production Mode Boundaries

11. **Academic Novelty, Honest Limitations, and Future Work**
    - 11.1 Academic Novelty Summary
    - 11.2 Real-World Limitations (Intermittent Demand, Dense Vector Indexing at Scale, Single-Node SQLite)
    - 11.3 Future Directions: Multi-Agent Consensus, Quantized On-Device SLMs, and Production Vector Databases

12. **Conclusion**

13. **References and Appendices**
    - Appendix A: Jinja2 Prompt Templates (v1 vs. v2 Full Text)
    - Appendix B: Pydantic Schema Definitions (`ExecutiveCommercialReport`)
    - Appendix C: Empirical Evaluation Scorecard Artifact
    - Appendix D: Architectural Decision Records (ADR-001 through ADR-014)
