// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
use keyring::Entry;
use serde::{Deserialize, Serialize};
use std::process::Command;

mod commands;
use commands::processing::{import_file, extract_steps, check_backend, generate_explanation, chat_about_explanation};

const SERVICE_NAME: &str = "math-algorithm-tool";

#[derive(Serialize, Deserialize, Debug)]
pub struct LaTeXExpression {
    latex: String,
    parsed: Option<String>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct Section {
    title: Option<String>,
    content: String,
    start_line: i32,
    end_line: i32,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct ProcessedInput {
    original_text: String,
    cleaned_text: String,
    latex_expressions: Vec<LaTeXExpression>,
    sections: Vec<Section>,
}

#[tauri::command]
fn set_api_key(provider: String, api_key: String) -> Result<(), String> {
    let entry = Entry::new(SERVICE_NAME, &provider)
        .map_err(|e| e.to_string())?;
    entry.set_password(&api_key).map_err(|e| e.to_string())
}

#[tauri::command]
fn get_api_key(provider: String) -> Result<String, String> {
    let entry = Entry::new(SERVICE_NAME, &provider)
        .map_err(|e| e.to_string())?;
    entry.get_password().map_err(|e| e.to_string())
}

#[tauri::command]
fn delete_api_key(provider: String) -> Result<(), String> {
    let entry = Entry::new(SERVICE_NAME, &provider)
        .map_err(|e| e.to_string())?;
    entry.delete_credential().map_err(|e| e.to_string())
}

#[tauri::command]
fn get_all_providers() -> Vec<String> {
    vec!["nvidia".to_string(), "openai".to_string(), "anthropic".to_string()]
}

#[tauri::command]
fn process_input(text: String) -> Result<ProcessedInput, String> {
    // Get the path to the Python script
    let script_dir = std::env::current_exe()
        .map(|p| p.parent().unwrap_or(std::path::Path::new(".")).to_path_buf())
        .unwrap_or_else(|_| std::path::PathBuf::from("."));
    
    // Try multiple paths for the Python processor
    let possible_paths = vec![
        script_dir.join("src/processing/text_processor.py"),
        std::path::PathBuf::from("src/processing/text_processor.py"),
        std::path::PathBuf::from("math-algorithm-tool/src/processing/text_processor.py"),
    ];
    
    let script_path = possible_paths
        .iter()
        .find(|p| p.exists())
        .cloned()
        .ok_or_else(|| "Could not find text_processor.py".to_string())?;
    
    // Run Python to process the input
    let output = Command::new("python3")
        .arg("-c")
        .arg(format!(
            r#"
import sys
sys.path.insert(0, '.')
from src.processing.text_processor import process_text_input
import json
import os

# Set path for imports
os.chdir('math-algorithm-tool')

result = process_text_input('''{}''')
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
            text.replace("'''", "\\'\\'\\'")
        ))
        .output()
        .map_err(|e| format!("Failed to run Python: {}", e))?;
    
    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(format!("Python error: {}", stderr));
    }
    
    let stdout = String::from_utf8_lossy(&output.stdout);
    let result: ProcessedInput = serde_json::from_str(&stdout)
        .map_err(|e| format!("Failed to parse result: {} - stdout: {}", e, stdout))?;
    
    Ok(result)
}

#[derive(Serialize, Deserialize, Debug)]
pub struct ExecutionResultRust {
    stdout: String,
    stderr: String,
    return_code: i32,
    timed_out: bool,
    memory_exceeded: bool,
    execution_time_ms: i32,
    error_message: Option<String>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct CodeGenerationResultRust {
    code: String,
    syntax_valid: bool,
    variable_mapping: std::collections::HashMap<String, String>,
    errors: Vec<String>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct VariableRust {
    name: String,
    #[serde(rename = "type")]
    var_type: String,
    #[serde(rename = "initialValue")]
    initial_value: Option<String>,
    description: Option<String>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct AlgorithmStepRust {
    #[serde(rename = "stepNumber")]
    step_number: i32,
    description: String,
    #[serde(rename = "codeEquivalent")]
    code_equivalent: String,
    variables: Vec<VariableRust>,
    #[serde(rename = "controlFlow")]
    control_flow: Option<String>,
    confidence: String,
    #[serde(rename = "confidenceReason")]
    confidence_reason: Option<String>,
}

#[tauri::command]
fn generate_python_code(steps: Vec<AlgorithmStepRust>) -> Result<CodeGenerationResultRust, String> {
    // Determine the working directory
    let script_dir = std::env::current_exe()
        .map(|p| p.parent().unwrap_or(std::path::Path::new(".")).to_path_buf())
        .unwrap_or_else(|_| std::path::PathBuf::from("."));
    
    let possible_cwds = vec![
        std::path::PathBuf::from("."),
        std::path::PathBuf::from("math-algorithm-tool"),
        script_dir.clone(),
    ];
    
    let cwd = possible_cwds.iter().find(|p| p.exists()).cloned().unwrap_or_else(|| std::path::PathBuf::from("."));
    
    // Convert steps to JSON for Python
    let steps_json = serde_json::to_string(&steps)
        .map_err(|e| format!("Failed to serialize steps: {}", e))?;
    
    // Run Python to generate code
    let output = Command::new("python3")
        .arg("-c")
        .arg(format!(
            r#"
import sys
import os
os.chdir('{}')
sys.path.insert(0, '.')
from src.processing.code_generator import generate_python_code, AlgorithmStep, Variable
import json

# Convert from TypeScript format to Python
steps = {}
python_steps = []
for s in steps.get('steps', []):
    vars = [Variable(name=v['name'], type=v.get('type', ''), initialValue=v.get('initialValue'), description=v.get('description')) for v in s.get('variables', [])]
    python_steps.append(AlgorithmStep(
        step_number=s['stepNumber'],
        description=s['description'],
        code_equivalent=s.get('codeEquivalent', ''),
        variables=vars,
        control_flow=s.get('controlFlow'),
        confidence=s.get('confidence', 'medium'),
        confidence_reason=s.get('confidenceReason')
    ))

result = generate_python_code(python_steps)
print(json.dumps({{
    'code': result.code,
    'syntax_valid': result.syntax_valid,
    'variable_mapping': result.variable_mapping,
    'errors': result.errors
}}))
"#,
            cwd.to_string_lossy().replace("'", "'\\''"),
            steps_json
        ))
        .current_dir(&cwd)
        .output()
        .map_err(|e| format!("Failed to run Python: {}", e))?;
    
    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(format!("Python error: {}", stderr));
    }
    
    let stdout = String::from_utf8_lossy(&output.stdout);
    let result: CodeGenerationResultRust = serde_json::from_str(&stdout)
        .map_err(|e| format!("Failed to parse result: {} - stdout: {}", e, stdout))?;
    
    Ok(result)
}

#[tauri::command]
fn execute_python(code: String, user_input: Option<String>) -> Result<ExecutionResultRust, String> {
    // Determine the working directory
    let script_dir = std::env::current_exe()
        .map(|p| p.parent().unwrap_or(std::path::Path::new(".")).to_path_buf())
        .unwrap_or_else(|_| std::path::PathBuf::from("."));
    
    // Try multiple paths for Python
    let possible_cwds = vec![
        std::path::PathBuf::from("."),
        std::path::PathBuf::from("math-algorithm-tool"),
        script_dir.clone(),
    ];
    
    let cwd = possible_cwds.iter().find(|p| p.exists()).cloned().unwrap_or_else(|| std::path::PathBuf::from("."));
    
    // Parse user_input if provided
    let user_input_arg = if let Some(ref input_str) = user_input {
        format!(", user_input={}", input_str)
    } else {
        String::new()
    };
    
    // Run Python to execute the code
    let output = Command::new("python3")
        .arg("-c")
        .arg(format!(
            r#"
import sys
import os
os.chdir('{}')
sys.path.insert(0, '.')
from src.processing.code_executor import execute_python
import json

result = execute_python('''{}'''{})
print(json.dumps({{
    'stdout': result.stdout,
    'stderr': result.stderr,
    'return_code': result.return_code,
    'timed_out': result.timed_out,
    'memory_exceeded': result.memory_exceeded,
    'execution_time_ms': result.execution_time_ms,
    'error_message': result.error_message
}}))
"#,
            cwd.to_string_lossy().replace("'", "'\\''"),
            code.replace("'''", "\\'\\'\\'"),
            user_input_arg
        ))
        .current_dir(&cwd)
        .output()
        .map_err(|e| format!("Failed to run Python: {}", e))?;
    
    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(format!("Python error: {}", stderr));
    }
    
    let stdout = String::from_utf8_lossy(&output.stdout);
    let result: ExecutionResultRust = serde_json::from_str(&stdout)
        .map_err(|e| format!("Failed to parse result: {} - stdout: {}", e, stdout))?;
    
    Ok(result)
}

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![
            greet,
            set_api_key,
            get_api_key,
            delete_api_key,
            get_all_providers,
            process_input,
            generate_python_code,
            execute_python,
            import_file,
            extract_steps,
            check_backend,
            generate_explanation,
            chat_about_explanation
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
