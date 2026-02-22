"""
DenseNet-121 Vision Model with Grad-CAM Explainability
Uses torchxrayvision pretrained weights on CheXpert (no training required)
"""

import torch
import torch.nn as nn
import numpy as np
import torchxrayvision as xrv
import torchvision.transforms as transforms
from PIL import Image
import cv2
import io
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

# 14 pathological conditions (CheXpert label set)
PATHOLOGY_LABELS = [
    "Atelectasis", "Cardiomegaly", "Consolidation", "Edema",
    "Effusion", "Emphysema", "Fibrosis", "Hernia",
    "Infiltration", "Mass", "Nodule", "Pleural_Thickening",
    "Pneumonia", "Pneumothorax",
]

SEVERITY_THRESHOLDS = {
    "URGENT": 0.85,
    "SEVERE": 0.70,
    "MODERATE": 0.50,
    "MILD": 0.30,
    "NORMAL": 0.0,
}

# Conditions that trigger URGENT alert regardless of threshold
URGENT_CONDITIONS = {"Pneumothorax", "Pneumonia", "Cardiomegaly"}


class GradCAM:
    """Gradient-weighted Class Activation Mapping for DenseBlock4."""

    def __init__(self, model: nn.Module):
        self.model = model
        self.gradients = None
        self.activations = None
        self._register_hooks()

    def _register_hooks(self):
        def forward_hook(module, input, output):
            self.activations = output.detach()

        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0].detach()

        # Hook into the last DenseBlock
        target_layer = self.model.model.features.denseblock4
        target_layer.register_forward_hook(forward_hook)
        target_layer.register_full_backward_hook(backward_hook)

    def generate(self, image_tensor: torch.Tensor, class_idx: int) -> np.ndarray:
        """Generate Grad-CAM heatmap for the given class index."""
        self.model.zero_grad()
        output = self.model(image_tensor)
        output[0, class_idx].backward()

        weights = self.gradients.mean(dim=[2, 3], keepdim=True)
        cam = (weights * self.activations).sum(dim=1, keepdim=True)
        cam = torch.relu(cam).squeeze().cpu().numpy()

        # Normalize and resize to input dimensions
        cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
        cam = cv2.resize(cam, (224, 224))
        return cam


class MediScanVisionModel:
    """DenseNet-121 inference pipeline with Grad-CAM explainability."""

    def __init__(self, model_name: str = "densenet121-res224-chex"):
        logger.info(f"Loading torchxrayvision model: {model_name}")
        self.model = xrv.models.DenseNet(weights=model_name)
        self.model.eval()
        self.grad_cam = GradCAM(self.model)
        self.transform = transforms.Compose([
            xrv.datasets.XRayCenterCrop(),
            xrv.datasets.XRayResizer(224),
        ])
        logger.info("✅ Vision model loaded successfully")

    def preprocess(self, image_bytes: bytes) -> torch.Tensor:
        """Convert uploaded image bytes to model-ready tensor."""
        img = Image.open(io.BytesIO(image_bytes)).convert("L")  # grayscale
        img_array = np.array(img)
        img_array = xrv.datasets.normalize(img_array, 255)
        img_array = img_array[None, ...]  # add channel dim
        img_tensor = torch.from_numpy(self.transform(img_array)).unsqueeze(0)
        return img_tensor

    def predict(self, image_bytes: bytes) -> Dict:
        """Run full inference: pathology detection + Grad-CAM + severity triage."""
        img_tensor = self.preprocess(image_bytes)

        with torch.no_grad():
            raw_output = self.model(img_tensor)

        probabilities = torch.sigmoid(raw_output).squeeze().cpu().numpy()

        conditions = [
            {"name": label, "confidence": float(prob)}
            for label, prob in zip(self.model.pathologies, probabilities)
            if label in PATHOLOGY_LABELS
        ]
        conditions.sort(key=lambda x: x["confidence"], reverse=True)

        # Severity triage
        severity = self._classify_severity(conditions)

        # Grad-CAM for top condition
        top_condition_idx = int(np.argmax(probabilities))
        heatmap = self.grad_cam.generate(img_tensor, top_condition_idx)

        return {
            "conditions": conditions,
            "severity": severity,
            "heatmap": heatmap,
            "top_condition": conditions[0]["name"] if conditions else "Normal",
        }

    def _classify_severity(self, conditions: List[Dict]) -> str:
        if not conditions:
            return "NORMAL"

        max_conf = conditions[0]["confidence"]
        top_name = conditions[0]["name"]

        if top_name in URGENT_CONDITIONS and max_conf > 0.70:
            return "URGENT"
        for severity, threshold in SEVERITY_THRESHOLDS.items():
            if max_conf >= threshold:
                return severity
        return "NORMAL"

    def generate_heatmap_overlay(
        self, original_bytes: bytes, heatmap: np.ndarray
    ) -> bytes:
        """Overlay Grad-CAM heatmap on original image and return as PNG bytes."""
        img = Image.open(io.BytesIO(original_bytes)).convert("RGB")
        img = img.resize((224, 224))
        img_array = np.array(img)

        heatmap_colored = cv2.applyColorMap(
            (heatmap * 255).astype(np.uint8), cv2.COLORMAP_JET
        )
        heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)

        overlay = cv2.addWeighted(img_array, 0.6, heatmap_colored, 0.4, 0)
        _, buffer = cv2.imencode(".png", overlay)
        return buffer.tobytes()


# Singleton — loaded once on startup
_model_instance = None


def get_vision_model() -> MediScanVisionModel:
    global _model_instance
    if _model_instance is None:
        _model_instance = MediScanVisionModel()
    return _model_instance
