"""
Tests for step extractor module.

Tests LLM-powered algorithm step extraction with mocked providers.
"""
import json
from unittest.mock import MagicMock, patch

import pytest

from src.processing.step_extractor import (
    AlgorithmStep,
    ExtractionResult,
    Variable,
    extract_steps,
    extract_steps_with_provider_name,
    STEP_EXTRACTION_SYSTEM_PROMPT,
    STEP_EXTRACTION_USER_PROMPT_TEMPLATE,
)
from src.processing.text_processor import ProcessedInput


class MockLLMProvider:
    """Mock LLM provider for testing."""

    def __init__(self, response_content: str = ""):
        self.response_content = response_content
        self.last_prompt = None
        self.last_system_prompt = None

    def generate(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ):
        from src.processing.llm_provider import LLMResponse
        self.last_prompt = prompt
        self.last_system_prompt = system_prompt
        return LLMResponse(
            content=self.response_content,
            provider="mock",
            model="mock-model",
        )

    def generate_json(self, prompt: str, system_prompt: str = None, temperature: float = 0.7, max_tokens: int = 4096):
        self.last_prompt = prompt
        self.last_system_prompt = system_prompt
        return json.loads(self.response_content)


class TestStepExtractorModels:
    """Tests for Pydantic models."""

    def test_variable_model(self):
        """Test Variable model creation."""
        var = Variable(
            name="x",
            type="int",
            initial_value="0",
            description="counter"
        )
        assert var.name == "x"
        assert var.type == "int"
        assert var.initial_value == "0"

    def test_algorithm_step_model(self):
        """Test AlgorithmStep model creation."""
        step = AlgorithmStep(
            step_number=1,
            description="Initialize counter",
            code_equivalent="x = 0",
            variables=[Variable(name="x", type="int", initial_value="0")],
            control_flow=None,
            confidence="high",
            confidence_reason=None,
        )
        assert step.step_number == 1
        assert step.confidence == "high"
        assert step.variables[0].name == "x"

    def test_algorithm_step_with_control_flow(self):
        """Test AlgorithmStep with control flow."""
        step = AlgorithmStep(
            step_number=2,
            description="Loop through elements",
            code_equivalent="for i in range(n):",
            variables=[],
            control_flow="for_loop",
            confidence="high",
            confidence_reason=None,
        )
        assert step.control_flow == "for_loop"

    def test_extraction_result_model(self):
        """Test ExtractionResult model."""
        steps = [
            AlgorithmStep(
                step_number=1,
                description="Test",
                code_equivalent="x = 1",
                confidence="high",
            )
        ]
        result = ExtractionResult(
            steps=steps,
            provider="openai",
            model="gpt-4o",
        )
        assert len(result.steps) == 1
        assert result.provider == "openai"


class TestStepExtraction:
    """Tests for step extraction functionality."""

    def test_extract_steps_success(self):
        """Test successful step extraction."""
        mock_response = {
            "steps": [
                {
                    "step_number": 1,
                    "description": "Initialize the sum to zero",
                    "code_equivalent": "sum = 0",
                    "variables": [
                        {"name": "sum", "type": "int", "initial_value": "0"}
                    ],
                    "control_flow": None,
                    "confidence": "high",
                    "confidence_reason": None,
                },
                {
                    "step_number": 2,
                    "description": "Loop through each element",
                    "code_equivalent": "for x in elements:",
                    "variables": [],
                    "control_flow": "for_loop",
                    "confidence": "high",
                    "confidence_reason": None,
                },
            ]
        }

        provider = MockLLMProvider(json.dumps(mock_response))
        processed_input = ProcessedInput(
            original_text="Sum all elements",
            cleaned_text="Sum all elements",
            latex_expressions=[],
            sections=[],
        )

        result = extract_steps(processed_input, provider)

        assert isinstance(result, ExtractionResult)
        assert len(result.steps) == 2
        assert result.steps[0].step_number == 1
        assert result.steps[0].confidence == "high"
        assert result.steps[1].control_flow == "for_loop"

    def test_extract_steps_with_latex(self):
        """Test extraction with LaTeX expressions."""
        mock_response = {
            "steps": [
                {
                    "step_number": 1,
                    "description": "Calculate sum using formula",
                    "code_equivalent": "result = sum(x)",
                    "variables": [],
                    "control_flow": None,
                    "confidence": "medium",
                    "confidence_reason": "The formula interpretation may vary",
                }
            ]
        }

        provider = MockLLMProvider(json.dumps(mock_response))
        processed_input = ProcessedInput(
            original_text="Sum formula: $\sum_{i=1}^n x_i$",
            cleaned_text="Sum formula: $sum_{i=1}^n x_i$",
            latex_expressions=[(r"\sum_{i=1}^n x_i", "sum(x)")],
            sections=[],
        )

        result = extract_steps(processed_input, provider)

        assert len(result.steps) == 1
        assert result.steps[0].confidence == "medium"
        # Verify LaTeX was included in prompt
        assert "sum" in provider.last_prompt.lower()

    def test_extract_steps_low_confidence(self):
        """Test extraction with low confidence."""
        mock_response = {
            "steps": [
                {
                    "step_number": 1,
                    "description": "Apply transformation (ambiguous)",
                    "code_equivalent": "transform(x)",
                    "variables": [],
                    "control_flow": None,
                    "confidence": "low",
                    "confidence_reason": "Multiple valid interpretations of transform()",
                }
            ]
        }

        provider = MockLLMProvider(json.dumps(mock_response))
        processed_input = ProcessedInput(
            original_text="Apply transform",
            cleaned_text="Apply transform",
            latex_expressions=[],
            sections=[],
        )

        result = extract_steps(processed_input, provider)

        assert result.steps[0].confidence == "low"
        assert result.steps[0].confidence_reason is not None

    def test_extract_steps_invalid_json(self):
        """Test extraction with invalid JSON response."""
        provider = MockLLMProvider("not valid json")
        processed_input = ProcessedInput(
            original_text="Test",
            cleaned_text="Test",
            latex_expressions=[],
            sections=[],
        )

        with pytest.raises(ValueError, match="Failed to parse"):
            extract_steps(processed_input, provider)

    def test_extract_steps_with_provider_name(self):
        """Test convenience function with provider name."""
        mock_response = {"steps": []}

        with patch("src.processing.step_extractor.get_provider") as mock_get_provider:
            mock_provider = MockLLMProvider(json.dumps(mock_response))
            mock_get_provider.return_value = mock_provider

            processed_input = ProcessedInput(
                original_text="Test",
                cleaned_text="Test",
                latex_expressions=[],
                sections=[],
            )

            result = extract_steps_with_provider_name(
                processed_input, "openai", "test-key"
            )

            mock_get_provider.assert_called_once_with("openai", "test-key")
            assert isinstance(result, ExtractionResult)


class TestPrompts:
    """Tests for extraction prompts."""

    def test_system_prompt_exists(self):
        """Test that system prompt is defined."""
        assert STEP_EXTRACTION_SYSTEM_PROMPT is not None
        assert "algorithm" in STEP_EXTRACTION_SYSTEM_PROMPT.lower()

    def test_user_prompt_template_exists(self):
        """Test that user prompt template is defined."""
        assert STEP_EXTRACTION_USER_PROMPT_TEMPLATE is not None
        assert "{text}" in STEP_EXTRACTION_USER_PROMPT_TEMPLATE
        assert "{latex}" in STEP_EXTRACTION_USER_PROMPT_TEMPLATE

    def test_user_prompt_template_renders(self):
        """Test that user prompt template renders correctly."""
        prompt = STEP_EXTRACTION_USER_PROMPT_TEMPLATE.format(
            text="Test text",
            latex="x + y",
        )
        assert "Test text" in prompt
        assert "x + y" in prompt
