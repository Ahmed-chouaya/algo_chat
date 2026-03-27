"""
Explanation generator module for generating plain language explanations of algorithms.

This module provides:
- Pydantic models for explanation results
- LLM-powered generation of algorithm explanations
- Three types of explanations: summary, step breakdowns, and code explanation

Uses the LLM provider pattern to support multiple providers (OpenAI, Anthropic, NVIDIA).
"""
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.processing.llm_provider import LLMProvider, get_provider
from src.processing.step_extractor import AlgorithmStep


class StepExplanation(BaseModel):
    """Explanation for a single algorithm step."""
    step_number: int
    explanation: str


class ExplanationResult(BaseModel):
    """Result of generating algorithm explanations."""
    summary: str  # One-paragraph overview of the algorithm
    step_explanations: list[StepExplanation]  # Explanation for each step
    code_explanation: str  # Plain language explanation of what the generated code does
    generated_at: datetime


# System prompt for explanation generation
EXPLANATION_SYSTEM_PROMPT = """You are an expert at explaining mathematical algorithms in plain language. 
Your task is to help users understand what algorithms do and how they work.

For each explanation:
1. Use simple, clear language accessible to someone who knows math but isn't a programmer
2. Focus on the "what" and "why" rather than implementation details
3. Avoid jargon where possible, or explain it when necessary
4. Connect steps to their mathematical purpose

Respond with valid JSON in the specified format."""


EXPLANATION_USER_PROMPT_TEMPLATE = """Generate explanations for the following algorithm:

**Algorithm Steps:**
{steps}

**Generated Python Code** (if available):
```{python}
{code}
```

Please provide a JSON response with this structure:
{{
  "summary": "A one-paragraph plain language summary of what this algorithm does and its purpose",
  "stepExplanations": [
    {{
      "stepNumber": 1,
      "explanation": "Plain language explanation of what this step does and why it's needed"
    }}
  ],
  "codeExplanation": "Plain language explanation of what the generated Python code does (not how it works)"
}}

Focus on making the explanations accessible to someone who knows mathematics but isn't a software developer.
Ensure the response is valid JSON."""


def generate_explanation(
    steps: list[AlgorithmStep],
    code: Optional[str],
    provider_name: str,
    api_key: str,
) -> ExplanationResult:
    """
    Generate plain language explanations for algorithm steps and code.

    Args:
        steps: List of algorithm steps to explain
        code: Optional generated Python code to explain
        provider_name: Name of provider ("openai", "anthropic", "nvidia")
        api_key: API key for the provider

    Returns:
        ExplanationResult with summary, step explanations, and code explanation

    Raises:
        ValueError: If explanation generation fails
    """
    # Format steps for the prompt
    steps_text = "\n".join(
        f"Step {step.step_number}: {step.description}"
        for step in steps
    )
    
    code_text = code if code else "No code generated yet."

    user_prompt = EXPLANATION_USER_PROMPT_TEMPLATE.format(
        steps=steps_text,
        code=code_text,
    )

    try:
        # Get JSON response from LLM
        provider = get_provider(provider_name, api_key)
        
        response_data = provider.generate_json(
            prompt=user_prompt,
            system_prompt=EXPLANATION_SYSTEM_PROMPT,
            temperature=0.5,  # Slightly higher for more natural explanations
            max_tokens=4096,
        )

        # Parse the explanations
        step_explanations = [
            StepExplanation(
                step_number=se["stepNumber"],
                explanation=se["explanation"]
            )
            for se in response_data.get("stepExplanations", [])
        ]

        return ExplanationResult(
            summary=response_data.get("summary", "No summary available."),
            step_explanations=step_explanations,
            code_explanation=response_data.get("codeExplanation", "No code explanation available."),
            generated_at=datetime.now(),
        )

    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse LLM response as JSON: {e}")
    except Exception as e:
        raise ValueError(f"Explanation generation failed: {e}")
