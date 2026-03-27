//! Processing commands for Tauri backend.
//!
//! Provides commands for:
//! - File import (PDF, TXT, MD)
//! - Algorithm step extraction via LLM
use keyring::Entry;
use serde::{Deserialize, Serialize};
use std::process::Command;
use tauri::command;

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
    // Run Python to import the file
    let output = Command::new("python3")
        .arg("-c")
        .arg(format!(
            r#"
import sys
sys.path.insert(0, 'math-algorithm-tool')
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
            path.replace("'", "'\\''")
        ))
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
    let process_output = Command::new("python3")
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
    let extract_output = Command::new("python3")
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
    let output = Command::new("python3")
        .arg("-c")
        .arg("import sys; sys.path.insert(0, 'math-algorithm-tool'); from src.processing import file_processor; print('ok')")
        .output()
        .map_err(|e| format!("Failed to check backend: {}", e))?;

    Ok(output.status.success())
}
