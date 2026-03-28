//! Processing commands for Tauri backend.
//!
//! Provides commands for:
//! - File import (PDF, TXT, MD)
//! - Algorithm step extraction via LLM
//! - Algorithm explanation generation via LLM
use keyring::Entry;
use serde::{Deserialize, Serialize};
use std::process::Command;
use tauri::command;

use crate::utils::get_python_command;

const SERVICE_NAME: &str = "math-algorithm-tool";

/// Supported file formats for import
#[derive(Debug, Serialize, Deserialize, Clone)]
#[serde(rename_all = "lowercase")]
pub enum SupportedFormat {
    Pdf,
    Txt,
    Md,
}

/// Result of importing a file
#[derive(Debug, Serialize, Deserialize)]
pub struct ImportResult {
    pub success: bool,
    pub format: SupportedFormat,
    pub content: String,
    #[serde(rename = "filePath")]
    pub file_path: String,
    pub error: Option<String>,
}

/// Variable in an algorithm step
#[derive(Debug, Serialize, Deserialize)]
pub struct Variable {
    pub name: String,
    #[serde(rename = "type")]
    pub var_type: String,
    #[serde(rename = "initialValue")]
    pub initial_value: Option<String>,
    pub description: Option<String>,
}

/// Control flow type
#[derive(Debug, Serialize, Deserialize, Clone)]
#[serde(rename_all = "snake_case")]
pub enum ControlFlow {
    ForLoop,
    WhileLoop,
    If,
    Elif,
}

/// Confidence level
#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Confidence {
    High,
    Medium,
    Low,
}

/// A single algorithm step
#[derive(Debug, Serialize, Deserialize)]
pub struct AlgorithmStep {
    #[serde(rename = "stepNumber")]
    pub step_number: i32,
    pub description: String,
    #[serde(rename = "codeEquivalent")]
    pub code_equivalent: String,
    pub variables: Vec<Variable>,
    #[serde(rename = "controlFlow")]
    pub control_flow: Option<ControlFlow>,
    pub confidence: Confidence,
    #[serde(rename = "confidenceReason")]
    pub confidence_reason: Option<String>,
}

/// Result of step extraction
#[derive(Debug, Serialize, Deserialize)]
pub struct ExtractionResult {
    pub steps: Vec<AlgorithmStep>,
    pub provider: String,
    pub model: String,
}

/// Import a file (PDF, TXT, or MD)
#[command]
pub fn import_file(path: String) -> Result<ImportResult, String> {
    // Determine the working directory (same pattern as other commands)
    let script_dir = std::env::current_exe()
        .map(|p| p.parent().unwrap_or(std::path::Path::new(".")).to_path_buf())
        .unwrap_or_else(|_| std::path::PathBuf::from("."));

    let possible_cwds = vec![
        std::path::PathBuf::from("math-algorithm-tool"),
        std::path::PathBuf::from("."),
        script_dir.clone(),
    ];

    let cwd = possible_cwds
        .iter()
        .find(|p| p.join("src/processing/file_processor.py").exists())
        .cloned()
        .unwrap_or_else(|| std::path::PathBuf::from("."));

    // Normalize path for cross-platform compatibility:
    // - Replace backslashes with forward slashes (Windows paths break Python string literals)
    // - Escape single quotes for safe Python string interpolation
    let safe_path = path.replace('\\', "/").replace("'", "\\'");

    // Run Python to import the file
    let output = Command::new(get_python_command())
        .arg("-c")
        .arg(format!(
            r#"
import sys
import os
sys.path.insert(0, '.')
import json
from src.processing.file_processor import import_file

result = import_file('{}')
print(json.dumps({{
    'success': result.success,
    'format': result.format.value,
    'content': result.content,
    'filePath': result.file_path,
    'error': result.error
}}))
"#,
            safe_path
        ))
        .current_dir(&cwd)
        .output()
        .map_err(|e| format!("Failed to run Python: {}", e))?;

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(format!("Python error: {}", stderr));
    }

    let stdout = String::from_utf8_lossy(&output.stdout);
    let result: ImportResult = serde_json::from_str(&stdout)
        .map_err(|e| format!("Failed to parse result: {} - stdout: {}", e, stdout))?;

    Ok(result)
}

/// Extract algorithm steps from text using LLM
#[command]
pub fn extract_steps(text: String, provider: String) -> Result<ExtractionResult, String> {
  // First process the text to extract LaTeX
  let process_output = Command::new(get_python_command())
        .arg("-c")
        .arg(format!(
            r#"
import sys
sys.path.insert(0, 'math-algorithm-tool')
import json
from src.processing.text_processor import process_text_input

result = process_text_input('{}')
print(json.dumps({{
    'original_text': result.original_text,
    'cleaned_text': result.cleaned_text,
    'latex_expressions': [
        {{'latex': latex, 'parsed': str(parsed) if parsed else None}}
        for latex, parsed in result.latex_expressions
    ],
    'sections': [
        {{'title': s.title, 'content': s.content, 'start_line': s.start_line, 'end_line': s.end_line}}
        for s in result.sections
    ]
}}))
"#,
            text.replace("'", "'\\''")
        ))
        .output()
        .map_err(|e| format!("Failed to process text: {}", e))?;

    if !process_output.status.success() {
        let stderr = String::from_utf8_lossy(&process_output.stderr);
        return Err(format!("Text processing error: {}", stderr));
    }

    let processed_json = String::from_utf8_lossy(&process_output.stdout);

    // Retrieve API key from secure storage
    let entry = Entry::new(SERVICE_NAME, &provider)
        .map_err(|e| format!("Failed to access keychain: {}", e))?;
    let api_key = entry.get_password()
        .map_err(|e| format!("API key not configured for {}. Please add it in Settings.", provider))?;

  // Now call the LLM to extract steps using the Python step_extractor
  let extract_output = Command::new(get_python_command())
        .arg("-c")
        .arg(format!(
            r#"
import sys
sys.path.insert(0, 'math-algorithm-tool')
import json

from src.processing.text_processor import ProcessedInput
from src.processing.step_extractor import extract_steps_with_provider_name

# Parse the processed data from text processing step
processed_json_data = '''{}'''
processed_data = json.loads(processed_json_data)
processed_input = ProcessedInput(**processed_data)

# Extract steps using LLM with API key
result = extract_steps_with_provider_name(
    processed_input,
    '{}',
    '{}'
)

print(json.dumps({{
    'steps': [{{
        'stepNumber': s.step_number,
        'description': s.description,
        'codeEquivalent': s.code_equivalent,
        'variables': [{{
            'name': v.name,
            'type': v.type,
            'initialValue': v.initial_value,
            'description': v.description
        }} for v in s.variables],
        'controlFlow': s.control_flow,
        'confidence': s.confidence,
        'confidenceReason': s.confidence_reason
    }} for s in result.steps],
    'provider': result.provider,
    'model': result.model
}}))
"#,
            processed_json.trim().replace("'''", "\\'\\'\\'"),
            provider,
            api_key.replace("'", "'\\''")
        ))
        .output()
        .map_err(|e| format!("Failed to extract steps: {}", e))?;

    if !extract_output.status.success() {
        let stderr = String::from_utf8_lossy(&extract_output.stderr);
        return Err(format!("Step extraction error: {}", stderr));
    }

    let stdout = String::from_utf8_lossy(&extract_output.stdout);
    let result: ExtractionResult = serde_json::from_str(&stdout)
        .map_err(|e| format!("Failed to parse result: {} - stdout: {}", e, stdout))?;

    Ok(result)
}

/// Check if the processing backend is available
#[command]
pub fn check_backend() -> Result<bool, String> {
  // Simple check - try to run a Python import
  let output = Command::new(get_python_command())
        .arg("-c")
        .arg("import sys; sys.path.insert(0, 'math-algorithm-tool'); from src.processing import file_processor; print('ok')")
        .output()
        .map_err(|e| format!("Failed to check backend: {}", e))?;

    Ok(output.status.success())
}

/// Explanation for a single step
#[derive(Debug, Serialize, Deserialize)]
pub struct StepExplanation {
    #[serde(rename = "stepNumber")]
    pub step_number: i32,
    pub explanation: String,
}

/// Result of explanation generation
#[derive(Debug, Serialize, Deserialize)]
pub struct ExplanationResult {
    pub summary: String,
    #[serde(rename = "stepExplanations")]
    pub step_explanations: Vec<StepExplanation>,
    #[serde(rename = "codeExplanation")]
    pub code_explanation: String,
    #[serde(rename = "generatedAt")]
    pub generated_at: String,
}

/// Generate explanation for algorithm steps and code using LLM
#[command]
pub fn generate_explanation(
    steps_json: String,
    code: Option<String>,
    provider: String,
) -> Result<ExplanationResult, String> {
    // Retrieve API key from secure storage
    let entry = Entry::new(SERVICE_NAME, &provider)
        .map_err(|e| format!("Failed to access keychain: {}", e))?;
    let api_key = entry.get_password()
        .map_err(|e| format!("API key not configured for {}. Please add it in Settings.", provider))?;

    // Call Python to generate explanation
  let code_arg = match &code {
    Some(c) => format!("Some(\"{}\")", c.replace("\"", "\\\"").replace("'", "\\'")),
    None => "None".to_string(),
  };

  let output = Command::new(get_python_command())
        .arg("-c")
        .arg(format!(
            r#"
import sys
sys.path.insert(0, 'math-algorithm-tool')
import json
from datetime import datetime

from src.processing.explanation_generator import generate_explanation

# Parse steps from JSON
steps_data = json.loads('''{}''')
steps = []
for s in steps_data.get('steps', []):
    from src.processing.step_extractor import AlgorithmStep, Variable, ControlFlow, Confidence
    variables = [Variable(**v) for v in s.get('variables', [])]
    step = AlgorithmStep(
        step_number=s['stepNumber'],
        description=s['description'],
        code_equivalent=s.get('codeEquivalent', ''),
        variables=variables,
        control_flow=s.get('controlFlow'),
        confidence=s.get('confidence', 'medium'),
        confidence_reason=s.get('confidenceReason')
    )
    steps.append(step)

code = {}

# Generate explanation
result = generate_explanation(steps, code, '{}', '{}')

print(json.dumps({{
    'summary': result.summary,
    'stepExplanations': [{{
        'stepNumber': se.step_number,
        'explanation': se.explanation
    }} for se in result.step_explanations],
    'codeExplanation': result.code_explanation,
    'generatedAt': result.generated_at.isoformat()
}}))
"#,
            steps_json.replace("'''", "\\'\\'\\'"),
            code_arg,
            provider,
            api_key.replace("'", "'\\''")
        ))
        .output()
        .map_err(|e| format!("Failed to generate explanation: {}", e))?;

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(format!("Explanation generation error: {}", stderr));
    }

    let stdout = String::from_utf8_lossy(&output.stdout);
    let result: ExplanationResult = serde_json::from_str(&stdout)
        .map_err(|e| format!("Failed to parse result: {} - stdout: {}", e, stdout))?;

    Ok(result)
}

/// Chat message for conversation history
#[derive(Debug, Serialize, Deserialize)]
pub struct ChatMessageInput {
    pub id: String,
    pub role: String,
    pub content: String,
}

/// Ask a follow-up question about the algorithm or code
#[command]
pub fn chat_about_explanation(
    question: String,
    algorithm_summary: String,
    steps_json: String,
    code_explanation: String,
    generated_code: Option<String>,
    history_json: String,
) -> Result<String, String> {
    // Retrieve API key - use a default provider
    let provider = "nvidia";
    let entry = Entry::new(SERVICE_NAME, provider)
        .map_err(|e| format!("Failed to access keychain: {}", e))?;
    let api_key = match entry.get_password() {
        Ok(key) => key,
        Err(_) => {
            // Try openai as fallback
            let entry = Entry::new(SERVICE_NAME, "openai")
                .map_err(|e| format!("Failed to access keychain: {}", e))?;
            entry.get_password()
                .map_err(|e| format!("API key not configured. Please add it in Settings.",))?
        }
    };

    // Call Python to handle chat
  let code_arg = match &generated_code {
    Some(c) => format!("Some(\"{}\")", c.replace("\"", "\\\"").replace("'", "\\'")),
    None => "None".to_string(),
  };

  let output = Command::new(get_python_command())
        .arg("-c")
        .arg(format!(
            r#"
import sys
sys.path.insert(0, 'math-algorithm-tool')
import json

from src.processing.explanation_generator import chat_about_explanation

# Parse steps from JSON
steps_data = json.loads('''{}''')
steps = []
for s in steps_data.get('steps', []):
    from src.processing.step_extractor import AlgorithmStep, Variable, ControlFlow, Confidence
    variables = [Variable(**v) for v in s.get('variables', [])]
    step = AlgorithmStep(
        step_number=s['stepNumber'],
        description=s['description'],
        code_equivalent=s.get('codeEquivalent', ''),
        variables=variables,
        control_flow=s.get('controlFlow'),
        confidence=s.get('confidence', 'medium'),
        confidence_reason=s.get('confidenceReason')
    )
    steps.append(step)

# Parse history
history_data = json.loads('''{}''')
history = []
for m in history_data.get('messages', []):
    from dataclasses import dataclass
    @dataclass
    class Msg:
        id: str
        role: str
        content: str
    history.append(Msg(id=m['id'], role=m['role'], content=m['content']))

code = {}

# Generate chat response
result = chat_about_explanation(
    question='{}',
    algorithm_summary='{}',
    steps=steps,
    code_explanation='{}',
    generated_code=code,
    history=history,
    provider='{}',
    api_key='{}'
)

print(json.dumps(result))
"#,
            steps_json.replace("'''", "\\'\\'\\'"),
            history_json.replace("'''", "\\'\\'\\'"),
            question.replace("'", "\\'"),
            algorithm_summary.replace("'", "\\'"),
            code_explanation.replace("'", "\\'"),
            code_arg,
            provider,
            api_key.replace("'", "\\'")
        ))
        .output()
        .map_err(|e| format!("Failed to chat: {}", e))?;

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(format!("Chat error: {}", stderr));
    }

    let stdout = String::from_utf8_lossy(&output.stdout);
    Ok(stdout.trim().to_string())
}
