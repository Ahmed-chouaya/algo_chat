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


# System prompt for chat follow-up questions
CHAT_SYSTEM_PROMPT = """You are an expert at explaining mathematical algorithms in plain language.
Your task is to answer follow-up questions about algorithms and their implementations.

Guidelines:
1. Use simple, clear language accessible to someone who knows math but isn't a programmer
2. Reference specific steps and code when relevant
3. If the user asks about a specific step (e.g., "Why does step 3 use recursion?"), provide contextual answer
4. Be concise but thorough - answer what was asked

Respond with valid JSON in this format:
{"response": "Your answer here"}"""


# User prompt template for chat
CHAT_USER_PROMPT_TEMPLATE = """Context:
- Algorithm Summary: {summary}

- Steps:
{steps}

- Code Explanation: {code_explanation}

- Generated Code (if available):
```{python}
{generated_code}
```

Previous conversation:
{history}

User's question: {question}

Provide a JSON response with your answer."""


def chat_about_explanation(
    question: str,
    algorithm_summary: str,
    steps: list[AlgorithmStep],
    code_explanation: str,
    generated_code: Optional[str],
    history: list,
    provider_name: str,
    api_key: str,
) -> str:
    """
    Answer a follow-up question about the algorithm or code.

    Args:
        question: User's follow-up question
        algorithm_summary: The algorithm summary from explanation generation
        steps: List of algorithm steps
        code_explanation: The code explanation from explanation generation
        generated_code: Optional generated Python code
        history: Previous chat messages
        provider_name: Name of provider ("openai", "anthropic", "nvidia")
        api_key: API key for the provider

    Returns:
        JSON string with the assistant's response

    Raises:
        ValueError: If chat fails
    """
    # Format steps for the prompt
    steps_text = "\n".join(
        f"Step {step.step_number}: {step.description}"
        for step in steps
    )

    # Format history
    history_text = ""
    if history:
        history_text = "\n".join(
            f"{msg.role}: {msg.content}"
            for msg in history[-10:]  # Last 10 messages
        )

    code_text = generated_code if generated_code else "No code generated yet."
    code_exp_text = code_explanation if code_explanation else "No code explanation available."

    user_prompt = CHAT_USER_PROMPT_TEMPLATE.format(
        summary=algorithm_summary,
        steps=steps_text,
        code_explanation=code_exp_text,
        generated_code=code_text,
        history=history_text,
        question=question,
    )

    try:
        provider = get_provider(provider_name, api_key)

        response_data = provider.generate_json(
            prompt=user_prompt,
            system_prompt=CHAT_SYSTEM_PROMPT,
            temperature=0.5,
            max_tokens=2048,
        )

        response = response_data.get("response", "I couldn't generate a response. Please try again.")

        return json.dumps({"response": response})

    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse LLM response as JSON: {e}")
    except Exception as e:
        raise ValueError(f"Chat failed: {e}")
