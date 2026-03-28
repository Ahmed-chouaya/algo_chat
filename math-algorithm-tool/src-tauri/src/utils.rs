//! Utility functions for cross-platform compatibility

/// Get the platform-appropriate Python command name
#[cfg(target_os = "windows")]
pub fn get_python_command() -> &'static str {
    "python"
}

#[cfg(not(target_os = "windows"))]
pub fn get_python_command() -> &'static str {
    "python3"
}
