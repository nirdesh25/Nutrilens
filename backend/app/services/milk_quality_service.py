import numpy as np
from typing import Dict, Any

# Quality label mapping: dataset uses 0=low, 1=medium, 2=high
_QUALITY_LABELS = {0: "low", 1: "medium", 2: "high"}
_QUALITY_DESC = {
    "high": "Milk is fresh and safe for consumption.",
    "medium": "Milk is acceptable but consume soon. Monitor conditions.",
    "low": "Milk is highly likely spoiled. Do not consume.",
}


class MilkQualityService:
    """
    Milk quality prediction using the trained RandomForest .pkl model.
    Falls back to heuristic rules if the model is not loaded.

    Input features (matching the Kaggle Milk Quality dataset):
        ph          - pH value (e.g. 6.5)
        temperature - Storage temperature in °C
        taste       - 1 = good, 0 = bad
        odor        - 1 = normal, 0 = abnormal
        fat         - 1 = normal fat content, 0 = abnormal
        turbidity   - 1 = clear, 0 = turbid
        color       - colour index value (dataset integer)
    """

    @staticmethod
    def predict_quality(
        ph: float,
        temperature: float,
        taste: int,
        odor: int,
        fat: int,
        turbidity: int,
        color: int,
    ) -> Dict[str, Any]:
        """Predict milk quality, preferring the trained sklearn model."""
        # Try to use the trained model from ml_service
        try:
            from app.services.ml_service import ml_service
            model = getattr(ml_service, 'milk_quality_model', None)
            if model is not None:
                features = np.array([[ph, temperature, taste, odor, fat, turbidity, color]])
                raw_pred = model.predict(features)[0]
                # Handle both string labels ('high'/'medium'/'low') and integer indices (0/1/2)
                if isinstance(raw_pred, (str, bytes)):
                    quality = str(raw_pred).lower()
                else:
                    pred_idx = int(raw_pred)
                    quality = _QUALITY_LABELS.get(pred_idx, "medium")
                # Get probability if available
                risk_score = 0
                reasons = []
                if hasattr(model, 'predict_proba'):
                    proba = model.predict_proba(features)[0]
                    # risk = probability of "low" quality (class 0)
                    low_idx = 0
                    risk_score = round(float(proba[low_idx]) * 10, 2)
                return {
                    "prediction": quality,
                    "risk_score": risk_score,
                    "reasons": reasons,
                    "description": _QUALITY_DESC.get(quality, "Analysis complete."),
                    "model": "trained_rf",
                }
        except Exception as e:
            print(f"[WARN] Milk quality model inference failed: {e} — using heuristics")

        # --- Heuristic fallback ---
        # Normal ranges: pH 6.5–6.7, temperature ≤ 4°C for fresh milk
        quality = "high"
        risk_score = 0
        reasons = []

        if ph < 6.4 or ph > 6.8:
            risk_score += 3
            reasons.append("Abnormal pH level")

        if temperature > 10:
            risk_score += 2
            reasons.append("High temperature could indicate spoilage")

        if odor == 0 or taste == 0:
            risk_score += 4
            reasons.append("Poor taste/odor detected")

        if fat == 0:
            risk_score += 1
            reasons.append("Abnormal fat content")

        if turbidity == 0:
            risk_score += 1
            reasons.append("Turbid appearance detected")

        if risk_score == 0:
            quality = "high"
        elif risk_score < 4:
            quality = "medium"
        else:
            quality = "low"

        return {
            "prediction": quality,
            "risk_score": risk_score,
            "reasons": reasons,
            "description": _QUALITY_DESC[quality],
            "model": "heuristic",
        }
