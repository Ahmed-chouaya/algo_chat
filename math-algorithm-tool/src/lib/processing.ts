/**
 * Processing module for algorithm text input.
 * 
 * Provides the interface to the Python backend for processing
 * algorithm descriptions, file imports, and step extraction.
 */
import { invoke } from '$lib/tauri-helper';

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

// File import types
export type SupportedFormat = 'pdf' | 'txt' | 'md';

export interface ImportResult {
  success: boolean;
  format: SupportedFormat;
  content: string;
  filePath: string;
  error: string | null;
}

// Step extraction types
export interface Variable {
  name: string;
  type: string;
  initialValue: string | null;
  description: string | null;
}

export type ControlFlow = 'for_loop' | 'while_loop' | 'if' | 'elif' | null;
export type Confidence = 'high' | 'medium' | 'low';

export interface AlgorithmStep {
  stepNumber: number;
  description: string;
  codeEquivalent: string;
  variables: Variable[];
  controlFlow: ControlFlow;
  confidence: Confidence;
  confidenceReason: string | null;
}

export interface ExtractionResult {
  steps: AlgorithmStep[];
  provider: string;
  model: string;
}

// Code generation types
export interface CodeGenerationResult {
  code: string;
  syntax_valid: boolean;
  variable_mapping: Record<string, string>;
  errors: string[];
}

// Code execution types
export interface ExecutionResult {
  stdout: string;
  stderr: string;
  return_code: number;
  timed_out: boolean;
  memory_exceeded: boolean;
  execution_time_ms: number;
  error_message: string | null;
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
 * Import a file (PDF, TXT, or MD) and extract its content.
 * 
 * @param path - Path to the file to import
 * @returns ImportResult with success status, format, and content
 */
export async function importFile(path: string): Promise<ImportResult> {
  try {
    const result = await invoke<ImportResult>('import_file', { path });
    return result;
  } catch (error) {
    console.error('Failed to import file:', error);
    throw error;
  }
}

/**
 * Extract algorithm steps from text using LLM.
 * 
 * @param text - Algorithm text to extract steps from
 * @param provider - LLM provider to use (openai, anthropic, nvidia)
 * @returns ExtractionResult with structured steps
 */
export async function extractAlgorithmSteps(text: string, provider: string): Promise<ExtractionResult> {
  try {
    const result = await invoke<ExtractionResult>('extract_steps', { text, provider });
    return result;
  } catch (error: any) {
    console.error('Failed to extract algorithm steps:', error);
    // Provide helpful error message for missing API key
    const errorStr = error?.toString?.() || String(error) || '';
    if (errorStr.includes('API key') || errorStr.includes('keychain') || errorStr.includes('Settings')) {
      throw new Error('API key not configured. Please go to Settings → API Keys to add your API key.');
    }
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
    const result = await invoke<boolean>('check_backend');
    return result;
  } catch {
    return false;
  }
}

/**
 * Execute Python code using the backend sandbox.
 * 
 * @param code - Python source code to execute
 * @param userInput - Optional user input to pass to the code via stdin
 * @returns ExecutionResult with stdout, stderr, and status flags
 */
export async function executePythonCode(code: string, userInput?: Record<string, unknown>): Promise<ExecutionResult> {
  try {
    const userInputJson = userInput ? JSON.stringify(userInput) : null;
    const result = await invoke<ExecutionResult>('execute_python', { 
      code, 
      userInput: userInputJson 
    });
    return result;
  } catch (error) {
    console.error('Failed to execute Python code:', error);
    return {
      stdout: '',
      stderr: '',
      return_code: -1,
      timed_out: false,
      memory_exceeded: false,
      execution_time_ms: 0,
      error_message: error?.toString() || 'Unknown error executing code'
    };
  }
}

/**
 * Generate Python code from algorithm steps.
 * 
 * @param steps - List of AlgorithmStep objects
 * @returns CodeGenerationResult with generated code and metadata
 */
export async function generatePythonCode(steps: AlgorithmStep[]): Promise<CodeGenerationResult> {
  try {
    const result = await invoke<CodeGenerationResult>('generate_python_code', { steps });
    return result;
  } catch (error) {
    console.error('Failed to generate Python code:', error);
    return {
      code: '',
      syntax_valid: false,
      variable_mapping: {},
      errors: [error?.toString() || 'Unknown error']
    };
  }
}
