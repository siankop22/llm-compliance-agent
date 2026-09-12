# LLM Compliance Document Agent

A RAG-based agent that retrieves relevant compliance documents, classifies risk, summarizes findings, and flags items for human review — with PII redaction and audit logging built in as guardrails.

## Pipeline
Synthetic docs → PII redaction (Presidio) → embeddings (sentence-transformers) → FAISS retrieval → Claude-based classification agent → audit log → evaluation

## Key Results
- **Guardrail evaluation:** PII redaction correctly caught names and emails, but missed an SSN and a masked account number on first pass — documented gap, not hidden, with a proposed regex-based fix
- **Output reliability:** Added a parsing guardrail after discovering the LLM wrapped JSON in markdown fences despite explicit instructions — a real lesson in not trusting strict schema compliance from an LLM
- **Operational metrics:** 33% human-review escalation rate, 0.92 average model confidence across test queries
- **Agent judgment:** Correctly distinguished a regulatory risk item (escalated) from routine complaint/informational queries (auto-resolved)

## Stack
Python, Anthropic API (Claude), sentence-transformers, FAISS, Microsoft Presidio

## What I'd change for production
- Custom regex recognizers for SSNs and account numbers to close the redaction gap
- Larger labeled eval set (10-20+ queries) with human-annotated ground truth for precision/recall on risk_category
- Structured output via a JSON schema/tool-calling instead of prompt-only formatting
