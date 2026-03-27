"""
Step extractor module for extracting algorithm steps from text using LLMs.

This module provides:
- Pydantic models for algorithm steps, variables, and confidence
- LLM-powered extraction of structured algorithm steps
- Confidence scoring with reasoning

Uses the LLM provider pattern to support multiple providers (OpenAI, Anthropic, NVIDIA).
"""
import json
from dataclasses import dataclass
from typing import Any, Optional

from pydantic import BaseModel

from src.processing.llm_provider import LLMProvider, get_provider
from src.processing.text_processor import ProcessedInput


# Pydantic models for structured output


class Variable(BaseModel):
    """Represents a variable in an algorithm step."""
    name: str
    type: str  # "int", "float", "list", "matrix", etc.
    initial_value: Optional[str] = None
    description: Optional[str] = None


class AlgorithmStep(BaseModel):
    """Represents a single step in an algorithm."""
    step_number: int
    description: str  # Plain language explanation
    code_equivalent: str  # Pseudocode for this step
    variables: list[Variable] = []
    control_flow: Optional[str] = None  # None, "for_loop", "while_loop", "if", "elif"
    confidence: str  # "high", "medium", "low"
    confidence_reason: Optional[str] = None  # Why this confidence level


class ExtractionResult(BaseModel):
    """Result of extracting algorithm steps."""
    steps: list[AlgorithmStep]
    raw_response: Optional[str] = None
    provider: str
    model: str


# System prompt for step extraction
STEP_EXTRACTION_SYSTEM_PROMPT = """You are an expert algorithm analyst. Your task is to analyze mathematical algorithm descriptions and break them down into clear, structured steps.

For each algorithm:
1. Extract numbered steps in order
2. Provide plain language explanations
3. Identify variables with their types and initial values
4. Mark control flow (loops, conditionals)
5. Rate confidence: high (unambiguous), medium (some interpretation needed), low (multiple valid interpretations)
6. Explain why medium/low confidence steps are ambiguous

Respond with valid JSON in the specified format."""


STEP_EXTRACTION_USER_PROMPT_TEMPLATE = """Extract the algorithm steps from the following text:

{text}

Extracted LaTeX expressions (if any):
{latex}

Please extract the algorithm as a JSON array of steps with this structure:
{{
  "steps": [
    {{
      "step_number": 1,
      "description": "Plain language explanation of this step",
      "code_equivalent": "Pseudocode for this step",
      "variables": [
        {{"name": "x", "type": "int", "initial_value": "0", "description": "counter variable"}}
      ],
      "control_flow": null or "for_loop" or "while_loop" or "if" or "elif",
      "confidence": "high" or "medium" or "low",
      "confidence_reason": "Why this confidence level" or null
    }}
  ]
}}

Ensure the response is valid JSON."""


def extract_steps(
    processed_input: ProcessedInput,
    provider: LLMProvider,
) -> ExtractionResult:
    """
    Extract algorithm steps from processed input using an LLM.

    Args:
        processed_input: ProcessedInput with cleaned text and extracted LaTeX
        provider: LLM provider to use for extraction

    Returns:
        ExtractionResult with structured steps

    Raises:
        ValueError: If extraction fails
    """
    # Build the prompt
    latex_str = "\n".join(
        f"- {latex}: {parsed}" 
        for latex, parsed in processed_input.latex_expressions
    ) if processed_input.latex_expressions else "No LaTeX expressions found."

    user_prompt = STEP_EXTRACTION_USER_PROMPT_TEMPLATE.format(
        text=processed_input.cleaned_text,
        latex=latex_str,
    )

    try:
        # Get JSON response from LLM
        response_data = provider.generate_json(
            prompt=user_prompt,
            system_prompt=STEP_EXTRACTION_SYSTEM_PROMPT,
            temperature=0.3,  # Lower temperature for more consistent output
            max_tokens=8192,
        )

        # Parse the steps
        steps_data = response_data.get("steps", [])
        steps = [AlgorithmStep(**step_data) for step_data in steps_data]

        # Get provider info
        provider_name = getattr(provider, "__class__", "Unknown").__name__.replace("Provider", "").lower()
        model_name = getattr(provider, "model", "unknown")

        return ExtractionResult(
            steps=steps,
            raw_response=json.dumps(response_data),
            provider=provider_name,
            model=model_name,
        )

    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse LLM response as JSON: {e}")
    except Exception as e:
        raise ValueError(f"Step extraction failed: {e}")


def extract_steps_with_provider_name(
    processed_input: ProcessedInput,
    provider_name: str,
    api_key: str,
) -> ExtractionResult:
    """
    Convenience function to extract steps with provider name and API key.

    Args:
        processed_input: ProcessedInput with cleaned text and extracted LaTeX
        provider_name: Name of provider ("openai", "anthropic", "nvidia")
        api_key: API key for the provider

    Returns:
        ExtractionResult with structured steps
    """
    provider = get_provider(provider_name, api_key)
    return extract_steps(processed_input, provider)
