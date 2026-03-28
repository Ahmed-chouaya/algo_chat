/**
 * Helper module for file dialogs with browser-only development support.
 *
 * Wraps @tauri-apps/plugin-dialog to provide helpful error messages
 * when running in browser-only mode instead of crashing.
 */

import { isTauri } from './tauri-helper';

// Type for the file dialog open function
export type OpenDialogOptions = {
  multiple?: boolean;
  filters?: Array<{
    name: string;
    extensions: string[];
  }>;
};

/**
 * Open a file dialog for selecting files.
 *
 * When running in Tauri, uses the real dialog from @tauri-apps/plugin-dialog.
 * When running in browser-only mode, throws a helpful error guiding developers
to use "npm run dev" instead of "npm run dev:vite".
 *
 * @param options - Dialog options
 * @returns Promise with selected file path(s)
 */
export async function open(options: OpenDialogOptions = {}): Promise<string | string[] | null> {
  if (!isTauri()) {
    throw new Error(
      'File dialogs require Tauri backend. ' +
      'Please run "npm run dev" to start the full Tauri application ' +
      'instead of "npm run dev:vite" for browser-only mode.'
    );
  }

  // Only import the real dialog when in Tauri environment
  const { open: realOpen } = await import('@tauri-apps/plugin-dialog');
  return realOpen(options);
}
