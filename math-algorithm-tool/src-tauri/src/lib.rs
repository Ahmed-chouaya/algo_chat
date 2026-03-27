// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
use keyring::Entry;
use serde::{Deserialize, Serialize};
use std::process::Command;

mod commands;
use commands::processing::{import_file, extract_steps, check_backend};

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
            import_file,
            extract_steps,
            check_backend
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
