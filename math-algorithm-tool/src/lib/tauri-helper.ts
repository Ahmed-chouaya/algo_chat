/**
 * Helper module for Tauri API invocations with browser-only development support.
 *
 * This module provides a wrapper around @tauri-apps/api/core that:
 * 1. Detects if the app is running in a Tauri environment
 * 2. Provides helpful error messages when running in browser-only mode
 * 3. Allows the app to function (with limitations) in both modes
 */

import { invoke as tauriInvoke } from '@tauri-apps/api/core';

/**
 * Check if the app is running inside a Tauri window
 */
export function isTauri(): boolean {
  return (
    typeof window !== 'undefined' &&
    !!(window as any).__TAURI_INTERNALS__
  );
}

/**
 * Wrapper around Tauri's invoke that provides browser-only development support.
 *
 * When running in browser-only mode (npm run dev:vite), this function provides
 * helpful error messages guiding developers to use "npm run dev" for full functionality.
 *
 * @param command - The Tauri command to invoke
 * @param args - Arguments to pass to the command
 * @returns Promise with the command result or a fallback value
 */
export async function invoke<T>(command: string, args?: any): Promise<T> {
  // Check if running in Tauri environment
  if (isTauri()) {
    // In Tauri, use the actual invoke function
    return tauriInvoke<T>(command, args);
  }

  // In browser-only mode, provide helpful error messages
  console.warn(`[Tauri Helper] Running in browser-only mode. Tauri command "${command}" requires native backend.`);
  console.warn('[Tauri Helper] To enable full functionality, run: npm run dev');

  // Provide appropriate fallback based on command
  switch (command) {
    case 'import_file':
      return {
        success: false,
        format: 'pdf',
        content: '',
        filePath: args?.path || '',
        error: 'File import requires Tauri backend. Please run "npm run dev" instead of "npm run:dev:vite"'
      } as T;

    case 'process_input':
      throw new Error(
        'Algorithm processing requires Tauri backend and Python processing. ' +
        'Please run "npm run dev" to start the full Tauri application.'
      );

    case 'extract_steps':
      throw new Error(
        'Step extraction requires Tauri backend and Python processing. ' +
        'Please run "npm run dev" to start the full Tauri application.'
      );

    case 'check_backend':
      return false as T;

    case 'generate_python_code':
      throw new Error(
        'Code generation requires Tauri backend and Python processing. ' +
        'Please run "npm run dev" to start the full Tauri application.'
      );

    case 'execute_python':
      throw new Error(
        'Python execution requires Tauri backend. ' +
        'Please run "npm run dev" to start the full Tauri application.'
      );

    case 'generate_explanation':
      throw new Error(
        'Explanation generation requires Tauri backend. ' +
        'Please run "npm run dev" to start the full Tauri application.'
      );

    case 'chat_about_explanation':
      throw new Error(
        'Chat functionality requires Tauri backend. ' +
        'Please run "npm run dev" to start the full Tauri application.'
      );

    case 'set_api_key':
    case 'get_api_key':
    case 'delete_api_key':
    case 'get_all_providers':
      throw new Error(
        'API key management requires Tauri backend for secure storage. ' +
        'Please run "npm run dev" to start the full Tauri application.'
      );

    default:
      throw new Error(
        `Tauri command "${command}" requires native backend. ` +
        `Please run "npm run dev" to start the full Tauri application.`
      );
  }
}

/**
 * Get a helpful message for browser-only development
 */
export function getBrowserModeMessage(): string {
  return 'Running in browser-only development mode. Some features require Tauri backend. Run "npm run dev" for full functionality.';
}
