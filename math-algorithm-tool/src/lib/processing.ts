/**
 * Processing module for algorithm text input.
 * 
 * Provides the interface to the Python backend for processing
 * algorithm descriptions.
 */
import { invoke } from '@tauri-apps/api/core';

export interface LaTeXExpression {
  latex: string;
  parsed: string | null;
}

export interface Section {
  title: string | null;
  content: string;
  start_line: number;
  end_line: number;
}

export interface ProcessedInput {
  original_text: string;
  cleaned_text: string;
  latex_expressions: LaTeXExpression[];
  sections: Section[];
}

/**
 * Process algorithm input text through the Python backend.
 * 
 * @param text - Raw text input containing algorithm description
 * @returns ProcessedInput with cleaned text, extracted LaTeX, and sections
 */
export async function processAlgorithmInput(text: string): Promise<ProcessedInput> {
  if (!text || !text.trim()) {
    return {
      original_text: '',
      cleaned_text: '',
      latex_expressions: [],
      sections: []
    };
  }

  try {
    const result = await invoke<ProcessedInput>('process_input', { text });
    return result;
  } catch (error) {
    console.error('Failed to process algorithm input:', error);
    throw error;
  }
}

/**
 * Check if the processing backend is available.
 * 
 * @returns true if backend is ready
 */
export async function checkProcessingBackend(): Promise<boolean> {
  try {
    await invoke('ping');
    return true;
  } catch {
    return false;
  }
}
