# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | ✅ Yes    |

## Reporting a Vulnerability

**Please do NOT open a public GitHub issue for security vulnerabilities.**

Email: `security@mediscan-ai.example.com`

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact

We'll respond within 48 hours and aim to patch within 7 days.

## Scope

- JWT authentication bypass
- Data exposure (PHI leakage)
- Dependency CVEs affecting PHI pipeline
- Azure Blob or GCP Cloud Run misconfigurations

## Out of Scope

- AI model accuracy or medical correctness (not a certified device)
- Rate limiting bypass for non-PHI endpoints
