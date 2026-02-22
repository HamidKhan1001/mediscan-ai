# 🩻 MediScan AI

<div align="center">

**Automated Medical Report Generation from Radiological Scans**

*Computer Vision · Natural Language Processing · Generative AI · HIPAA-Aligned Architecture*

---

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://reactjs.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.x-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![HuggingFace](https://img.shields.io/badge/🤗-Transformers-FFD21E)](https://huggingface.co/)

[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![GCP](https://img.shields.io/badge/GCP-Cloud%20Run-4285F4?logo=googlecloud&logoColor=white)](https://cloud.google.com/run)
[![Azure](https://img.shields.io/badge/Azure-Blob%20Storage-0078D4?logo=microsoftazure&logoColor=white)](https://azure.microsoft.com/)
[![CI/CD](https://img.shields.io/github/actions/workflow/status/YOUR_USERNAME/mediscan-ai/ci.yml?label=CI%2FCD&logo=githubactions&logoColor=white)](https://github.com/YOUR_USERNAME/mediscan-ai/actions)
[![codecov](https://img.shields.io/badge/coverage-pytest-brightgreen?logo=pytest)](https://github.com/YOUR_USERNAME/mediscan-ai)
[![W&B](https://img.shields.io/badge/Tracked%20with-W%26B-FFBE00?logo=weightsandbiases&logoColor=black)](https://wandb.ai/)

[![FHIR](https://img.shields.io/badge/HL7-FHIR%20R4-E84C3D)](https://www.hl7.org/fhir/)
[![HIPAA](https://img.shields.io/badge/HIPAA-Aligned%20Prototype-0097A7)](https://www.hhs.gov/hipaa/index.html)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![GitHub Stars](https://img.shields.io/github/stars/YOUR_USERNAME/mediscan-ai?style=social)](https://github.com/YOUR_USERNAME/mediscan-ai/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/YOUR_USERNAME/mediscan-ai?style=social)](https://github.com/YOUR_USERNAME/mediscan-ai/network/members)
[![Issues](https://img.shields.io/github/issues/YOUR_USERNAME/mediscan-ai)](https://github.com/YOUR_USERNAME/mediscan-ai/issues)

</div>

---

> ⚠️ **Academic Disclaimer:** MediScan AI is developed for academic, research, and portfolio demonstration purposes as the Final Project for [Atomcamp AI Bootcamp Cohort 15](https://atomcamp.com). It is **NOT** a certified medical device and has **NOT** been approved by the FDA or any regulatory authority. All generated reports must not be used as a substitute for professional medical diagnosis.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [API Reference](#-api-reference)
- [HIPAA Alignment](#-hipaa-alignment)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [Roadmap](#-roadmap)
- [License](#-license)

---

## 🔭 Overview

MediScan AI is a **multimodal AI system** that accepts chest X-rays, MRI scans, and retinal images as input and automatically generates structured, clinician-readable radiology reports in natural language.

The system addresses a critical global healthcare gap — the WHO estimates a deficit of over **1 million trained radiologists**, with average report turnaround exceeding **24–48 hours** in under-resourced settings. MediScan AI delivers AI-assisted diagnostic support that is affordable, explainable, and deployable with minimal infrastructure.

| Metric | Status Quo | MediScan AI |
|--------|------------|-------------|
| Report Turnaround | 24–48 hours | < 30 seconds |
| Cost per Report | $150–300 | Near-zero marginal cost |
| Radiologist Required | Yes | AI-assisted support |
| Explainability | Black box | Grad-CAM heatmaps |

---

## ✨ Features

- **🖼️ Multimodal Image Input** — Drag-and-drop upload for JPEG/PNG chest X-rays and MRI slices
- **🧠 AI Abnormality Detection** — DenseNet-121 (CheXpert pretrained) detects **14 pathological conditions** including Pneumonia, Pleural Effusion, Cardiomegaly, and Pneumothorax
- **📝 Automated Report Generation** — BioGPT via HuggingFace generates structured reports with Technique, Findings, Impression, and Recommendation sections
- **🔥 Grad-CAM Explainability** — Gradient-weighted Class Activation Maps highlight anatomical regions of concern
- **🚨 Severity Triage** — Auto-classification: Normal / Mild / Moderate / Severe / **URGENT** with colour-coded alerts
- **☁️ Multi-Cloud Infrastructure** — FastAPI on GCP Cloud Run + Azure Blob Storage (AES-256 encrypted)
- **📄 FHIR-Compatible Output** — Reports exportable in HL7 FHIR DiagnosticReport format for EMR/EHR integration
- **🔁 CI/CD Pipeline** — GitHub Actions: test → Docker build → deploy to GCP Cloud Run on every push

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│         React 18 Frontend (TailwindCSS + Vite)       │
│   Drag-drop upload · Heatmap toggle · PDF download   │
└──────────────────────┬──────────────────────────────┘
                       │ HTTPS TLS 1.3
                       ▼
┌─────────────────────────────────────────────────────┐
│          GCP Cloud Run — FastAPI Backend              │
│    JWT Auth · Rate Limiter · HIPAA Audit Logger       │
│                       │                              │
│   ┌───────────────────┼───────────────────┐          │
│   ▼                   ▼                   ▼          │
│ DenseNet-121       BioGPT NLP       Azure Blob        │
│ (torchxrayvision)  (HuggingFace)    AES-256 Storage   │
│ + Grad-CAM         + FHIR Format    + Key Vault       │
└─────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│         GitHub Actions CI/CD Pipeline                 │
│   pytest → Docker build → Artifact Registry → Deploy  │
└─────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Vision AI | PyTorch + DenseNet-121 (torchxrayvision) | 14-condition X-ray classification |
| Generative AI | BioGPT (HuggingFace Transformers) | Structured report generation |
| Explainability | Grad-CAM + OpenCV | Anatomical attention heatmaps |
| Backend | FastAPI + Uvicorn + Pydantic | Async REST API, JWT auth |
| Frontend | React 18 + TailwindCSS + Vite | Drag-drop UI, heatmap toggle |
| ML Tracking | Weights & Biases (W&B) | Experiment logs, model versioning |
| Containers | Docker + Docker Compose | Reproducible builds |
| Cloud Compute | GCP Cloud Run | Serverless auto-scaling backend |
| Cloud Storage | Azure Blob + Azure Key Vault | AES-256 encrypted image storage |
| CI/CD | GitHub Actions | Automated test & deploy pipeline |
| Medical Standards | HL7 FHIR DiagnosticReport | EMR/EHR-compatible output |
| Testing | pytest + Locust | Unit tests + load testing |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker + Docker Compose
- GCP account (for cloud deploy)
- Azure account (for blob storage)

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/mediscan-ai.git
cd mediscan-ai
```

### 2. Environment Setup

```bash
cp .env.example .env
# Fill in your API keys and cloud credentials
```

### 3. Run with Docker Compose (Recommended)

```bash
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 4. Run Backend Locally

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 5. Run Frontend Locally

```bash
cd frontend
npm install
npm run dev
```

### 6. Run Tests

```bash
cd backend
pytest tests/ -v --cov=app
```

---

## 📡 API Reference

### `POST /api/v1/analyze`
Upload a radiological scan for AI analysis.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Authorization: Bearer <token>" \
  -F "file=@chest_xray.jpg"
```

**Response:**
```json
{
  "scan_id": "uuid",
  "severity": "MODERATE",
  "conditions": [
    {"name": "Pneumonia", "confidence": 0.87},
    {"name": "Pleural Effusion", "confidence": 0.43}
  ],
  "report": {
    "technique": "PA chest radiograph",
    "findings": "There is increased opacity in the right lower lobe...",
    "impression": "Findings consistent with right lower lobe pneumonia.",
    "recommendation": "Clinical correlation recommended. Follow-up imaging in 4-6 weeks."
  },
  "heatmap_url": "https://storage.azure.com/...",
  "fhir_report_url": "https://storage.azure.com/..."
}
```

### `GET /api/v1/health`
Health check endpoint.

### `GET /api/v1/reports/{scan_id}`
Retrieve a previously generated report.

Full API documentation available at `/docs` (Swagger UI) when running locally.

---

## 🔐 HIPAA Alignment

> ⚠️ These are **prototype-level** implementations demonstrating enterprise architectural thinking. This is **NOT** a certified HIPAA-compliant product. Formal review and legal assessment are required before any production or clinical deployment.

| Safeguard | Regulation | MVP Implementation |
|-----------|-----------|-------------------|
| Access Controls | §164.312(a)(1) | JWT + RBAC via FastAPI middleware |
| Audit Controls | §164.312(b) | All requests logged to GCP Cloud Logging |
| Transmission Security | §164.312(e)(1) | TLS 1.3 enforced, HTTPS-only |
| Encryption at Rest | §164.312(a)(2)(iv) | Azure Blob AES-256 + Key Vault |
| Data De-identification | §164.514(b) | EXIF + DICOM tags stripped pre-processing |
| Data Retention | §164.310(d)(2) | Auto-delete after 30 days (Azure lifecycle) |
| Minimum Necessary | §164.502(b) | Only image data collected, no unnecessary PHI |

**Additional Safeguards:**
- ✅ No real patient data — MVP uses anonymised CheXpert public samples only
- ✅ Mandatory disclaimer on every generated report
- ✅ No model training on user data without explicit written consent
- ✅ GCP + Azure HIPAA BAAs available (must be signed before any PHI processing)

---

## 📁 Project Structure

```
mediscan-ai/
├── .github/
│   └── workflows/
│       ├── ci.yml              # CI: test + lint on PR
│       └── deploy.yml          # CD: Docker build + GCP Cloud Run deploy
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── analyze.py      # /analyze endpoint
│   │   │   ├── auth.py         # JWT auth endpoints
│   │   │   └── reports.py      # Report retrieval
│   │   ├── core/
│   │   │   ├── config.py       # Settings (pydantic-settings)
│   │   │   ├── security.py     # JWT + RBAC logic
│   │   │   └── logging.py      # HIPAA audit logger
│   │   ├── models/
│   │   │   ├── densenet.py     # DenseNet-121 + Grad-CAM
│   │   │   └── biogpt.py       # BioGPT report generator
│   │   ├── services/
│   │   │   ├── storage.py      # Azure Blob Storage client
│   │   │   ├── fhir.py         # FHIR DiagnosticReport formatter
│   │   │   └── triage.py       # Severity classification
│   │   └── main.py             # FastAPI app entrypoint
│   ├── tests/
│   │   ├── test_analyze.py
│   │   ├── test_auth.py
│   │   └── test_models.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── UploadZone.jsx  # Drag-drop upload
│   │   │   ├── HeatmapView.jsx # Grad-CAM overlay toggle
│   │   │   ├── ReportCard.jsx  # Structured report display
│   │   │   └── SeverityBanner.jsx
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   └── Login.jsx
│   │   └── App.jsx
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── LICENSE
└── README.md
```

---

## 🗺️ Roadmap

| Priority | Enhancement | Est. Effort |
|----------|------------|-------------|
| 🔴 High | Full CheXpert Fine-Tuning (224K scans) | 3–4 weeks |
| 🔴 High | BioGPT Fine-Tuning on MIMIC-CXR (227K records) | 2–3 weeks |
| 🔴 High | Formal HIPAA Production Audit | Ongoing |
| 🟡 Med | Native DICOM (.dcm) Support via pydicom | 1 week |
| 🟡 Med | Doctor Feedback Loop (radiologist corrections) | 2 weeks |
| 🟡 Med | Scan History Dashboard | 1–2 weeks |
| 🟢 Low | CT Scan & MRI Support (3D CNNs: Med3D, SwinUNETR) | 4–6 weeks |
| 🟢 Low | Mobile App (React Native) | 4–5 weeks |
| 🟢 Low | Hospital EMR Integration (Epic, Cerner) | 6–8 weeks |
| 🟢 Low | Multi-language Reports (Urdu, Arabic) | 2–3 weeks |

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a PR.

```bash
# 1. Fork the repo
# 2. Create your feature branch
git checkout -b feature/amazing-feature

# 3. Commit your changes
git commit -m 'feat: add amazing feature'

# 4. Push to the branch
git push origin feature/amazing-feature

# 5. Open a Pull Request
```

We follow [Conventional Commits](https://www.conventionalcommits.org/) and [Semantic Versioning](https://semver.org/).

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Syed Hassan Tayyab**
- Atomcamp AI Bootcamp Cohort 15 — Final Project
- Module: Computer Vision & NLP | February 2026

---

<div align="center">

⭐ **If this project helped you, please give it a star!** ⭐

Made with ❤️ for open-source medical AI

</div>
