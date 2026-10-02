#!/usr/bin/env python3
"""Sentiment Analysis Module — lấy từ JensBender/youtube-channel-analytics.

Models:
- RoBERTa: cardiffnlp/twitter-roberta-base-sentiment-latest (3-class)
- DistilBERT: distilbert-base-uncased-finetuned-sst-2-english (2-class)

Usage:
    from sentiment_analyzer import SentimentAnalyzer
    analyzer = SentimentAnalyzer(model="roberta")
    result = analyzer.analyze("This is great!")
    # {"label": "positive", "score": 0.98}
"""
from __future__ import annotations

import logging
from typing import Literal

logger = logging.getLogger(__name__)

# Lazy import — chỉ load transformers khi cần
_pipeline = None
_model_name = None


def _get_pipeline(model: Literal["roberta", "distilbert"] = "roberta"):
    """Lazy load pipeline (tránh load khi không dùng)."""
    global _pipeline, _model_name
    if _pipeline is not None and _model_name == model:
        return _pipeline

    try:
        from transformers import pipeline
    except ImportError:
        raise ImportError(
            "transformers not installed. Run: pip install transformers torch"
        )

    if model == "roberta":
        model_id = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    else:
        model_id = "distilbert-base-uncased-finetuned-sst-2-english"

    logger.info(f"Loading sentiment model: {model_id}")
    _pipeline = pipeline(
        task="sentiment-analysis",
        model=model_id,
        truncation=True,
        max_length=512,
    )
    _model_name = model
    return _pipeline


class SentimentAnalyzer:
    """Sentiment analysis cho YouTube comments."""

    def __init__(self, model: Literal["roberta", "distilbert"] = "roberta"):
        self.model = model
        self._pipeline = None

    @property
    def pipeline(self):
        if self._pipeline is None:
            self._pipeline = _get_pipeline(self.model)
        return self._pipeline

    def analyze(self, text: str) -> dict:
        """Analyze sentiment của 1 comment.

        Returns:
            {"label": "positive"|"negative"|"neutral", "score": 0.0-1.0}
        """
        if not text or not text.strip():
            return {"label": "neutral", "score": 0.0}

        try:
            result = self.pipeline(text[:512])[0]
            return {
                "label": result["label"].lower(),
                "score": round(result["score"], 3),
            }
        except Exception as e:
            logger.error(f"Error analyzing: {text[:50]}... {e}")
            return {"label": "error", "score": 0.0}

    def analyze_batch(self, texts: list[str]) -> list[dict]:
        """Analyze sentiment của nhiều comments.

        Returns:
            List of {"label": ..., "score": ...}
        """
        if not texts:
            return []

        # Filter empty texts
        valid_texts = [t[:512] for t in texts if t and t.strip()]
        if not valid_texts:
            return [{"label": "neutral", "score": 0.0} for _ in texts]

        try:
            results = self.pipeline(valid_texts)
            return [
                {"label": r["label"].lower(), "score": round(r["score"], 3)}
                for r in results
            ]
        except Exception as e:
            logger.error(f"Batch error: {e}")
            return [{"label": "error", "score": 0.0} for _ in texts]

    def analyze_with_id(self, comments: list[dict]) -> list[dict]:
        """Analyze sentiment và trả về kèm comment_id.

        Input: [{"comment_id": "...", "comment_text": "..."}, ...]
        Output: [{"comment_id": "...", "sentiment": "...", "confidence": ...}, ...]
        """
        if not comments:
            return []

        texts = [c.get("comment_text", "") for c in comments]
        results = self.analyze_batch(texts)

        output = []
        for c, r in zip(comments, results):
            output.append({
                "comment_id": c.get("comment_id", ""),
                "sentiment": r["label"],
                "confidence": r["score"],
            })
        return output


if __name__ == "__main__":
    # Test nhanh
    logging.basicConfig(level=logging.INFO)
    analyzer = SentimentAnalyzer(model="roberta")

    test_comments = [
        "This is amazing! Thanks for the video.",
        "I lost all my money following this advice.",
        "Great analysis, very helpful.",
        "This is terrible, don't listen to him.",
        "Neutral comment about trading.",
    ]

    print("Testing sentiment analysis:")
    for text in test_comments:
        result = analyzer.analyze(text)
        print(f"  {text[:50]:50} → {result['label']:10} ({result['score']:.3f})")
