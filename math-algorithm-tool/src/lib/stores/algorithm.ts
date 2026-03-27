/**
 * Store for algorithm step state and confirmation tracking.
 * 
 * Manages the extracted steps, confirmation status, and processing state.
 */
import { writable } from 'svelte/store';
import type { AlgorithmStep, CodeGenerationResult, ExecutionResult } from '$lib/processing';

export interface AlgorithmState {
  steps: AlgorithmStep[];
  confirmed: boolean;
  isProcessing: boolean;
  generatedCode: string | null;
  codeGenerationResult: CodeGenerationResult | null;
  executionResult: ExecutionResult | null;
  isExecuting: boolean;
}

const initialState: AlgorithmState = {
  steps: [],
  confirmed: false,
  isProcessing: false,
  generatedCode: null,
  codeGenerationResult: null,
  executionResult: null,
  isExecuting: false
};

function createAlgorithmStore() {
  const { subscribe, set, update } = writable<AlgorithmState>(initialState);

  return {
    subscribe,
    
    /** Set extracted steps and reset confirmation */
    setSteps: (steps: AlgorithmStep[]) => 
      update(state => ({ ...state, steps, confirmed: false })),
    
    /** Mark steps as confirmed by user */
    confirm: () => 
      update(state => ({ ...state, confirmed: true })),
    
    /** Reset to initial state */
    reset: () => set(initialState),
    
    /** Update processing state */
    setProcessing: (isProcessing: boolean) => 
      update(state => ({ ...state, isProcessing })),
    
    /** Set generated code */
    setGeneratedCode: (code: string, generationResult: CodeGenerationResult | null) =>
      update(state => ({ ...state, generatedCode: code, codeGenerationResult: generationResult })),
    
    /** Set execution result */
    setExecutionResult: (result: ExecutionResult | null) =>
      update(state => ({ ...state, executionResult: result })),
    
    /** Set executing state */
    setExecuting: (isExecuting: boolean) =>
      update(state => ({ ...state, isExecuting }))
  };
}

export const algorithmStore = createAlgorithmStore();
