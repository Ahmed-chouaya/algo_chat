// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
use keyring::Entry;

const SERVICE_NAME: &str = "math-algorithm-tool";

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
            get_all_providers
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
