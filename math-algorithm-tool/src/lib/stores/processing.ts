/**
 * Store for algorithm processing state.
 * 
 * Shares processed algorithm data between InputPanel and OutputPanel.
 */
import { writable } from 'svelte/store';
import type { ProcessedInput } from './processing';

/** Initial empty state */
const initialState: ProcessedInput = {
  original_text: '',
  cleaned_text: '',
  latex_expressions: [],
  sections: []
};

/** Writable store for processed algorithm input */
export const processedInput = writable<ProcessedInput>(initialState);

/** Store for loading state during processing */
export const isProcessing = writable<boolean>(false);

/** Store for error messages */
export const processingError = writable<string | null>(null);

/** Reset to initial state */
export function resetProcessing() {
  processedInput.set(initialState);
  processingError.set(null);
  isProcessing.set(false);
}
