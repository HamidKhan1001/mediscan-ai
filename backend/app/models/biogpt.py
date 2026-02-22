"""
BioGPT NLP Report Generator
Uses Microsoft BioGPT via HuggingFace to generate structured radiology reports
"""

from transformers import pipeline, BioGptTokenizer, BioGptForCausalLM
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

REPORT_DISCLAIMER = (
    "\n\n⚠️ DISCLAIMER: This AI-generated report is for educational and research "
    "purposes only and does not constitute medical advice or a clinical diagnosis. "
    "Always consult a qualified radiologist or physician."
)

SEVERITY_RECOMMENDATIONS = {
    "URGENT": "URGENT: Immediate clinical review required. Please escalate to attending physician.",
    "SEVERE": "Prompt clinical correlation recommended. Specialist referral advised within 24–48 hours.",
    "MODERATE": "Clinical correlation recommended. Follow-up imaging in 4–6 weeks advised.",
    "MILD": "Findings noted. Routine follow-up recommended at next scheduled visit.",
    "NORMAL": "No acute cardiopulmonary findings. Routine follow-up as clinically indicated.",
}


class BioGPTReportGenerator:
    """Generates structured radiology reports from vision model outputs."""

    def __init__(self, model_name: str = "microsoft/biogpt"):
        logger.info(f"Loading BioGPT model: {model_name}")
        self.tokenizer = BioGptTokenizer.from_pretrained(model_name)
        self.model = BioGptForCausalLM.from_pretrained(model_name)
        self.generator = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            max_new_tokens=200,
        )
        logger.info("✅ BioGPT model loaded successfully")

    def generate_report(
        self,
        conditions: List[Dict],
        severity: str,
        scan_type: str = "chest X-ray",
    ) -> Dict[str, str]:
        """
        Generate a structured radiology report.

        Returns a dict with sections:
          - technique, findings, impression, recommendation
        """
        significant = [c for c in conditions if c["confidence"] > 0.30]
        normal = len(significant) == 0

        technique = f"PA {scan_type}. AI-assisted analysis performed using DenseNet-121 with CheXpert pretrained weights."

        if normal:
            findings_text = "No acute cardiopulmonary findings identified. Lung fields appear clear bilaterally."
            impression_text = "Normal chest radiograph. No acute disease identified."
        else:
            # Build BioGPT prompt from detected conditions
            condition_list = ", ".join(
                [f"{c['name']} ({c['confidence']:.0%})" for c in significant[:5]]
            )
            prompt = (
                f"Radiology report findings for a patient with {condition_list}: "
                f"The chest radiograph demonstrates"
            )
            generated = self.generator(prompt, do_sample=False)[0]["generated_text"]
            # Strip the prompt from output
            findings_text = generated[len(prompt):].strip().split(".")[0:3]
            findings_text = ". ".join(findings_text).strip() + "."

            top = significant[0]
            impression_text = (
                f"Findings most consistent with {top['name']} "
                f"(confidence {top['confidence']:.0%}). "
                f"Severity classification: {severity}."
            )

        recommendation = SEVERITY_RECOMMENDATIONS.get(severity, SEVERITY_RECOMMENDATIONS["NORMAL"])

        return {
            "technique": technique,
            "findings": findings_text,
            "impression": impression_text,
            "recommendation": recommendation,
            "disclaimer": REPORT_DISCLAIMER.strip(),
        }


# Singleton
_generator_instance = None


def get_report_generator() -> BioGPTReportGenerator:
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = BioGPTReportGenerator()
    return _generator_instance
