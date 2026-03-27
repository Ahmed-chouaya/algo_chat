/**
 * Store for algorithm step state and confirmation tracking.
 * 
 * Manages the extracted steps, confirmation status, and processing state.
 */
import { writable } from 'svelte/store';
import type { AlgorithmStep, CodeGenerationResult, ExecutionResult } from '$lib/processing';

/** Explanation state for an algorithm */
export interface StepExplanation {
  stepNumber: number;
  explanation: string;
}

/** Chat message for follow-up questions */
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface ExplanationState {
  summary: string;
  stepExplanations: StepExplanation[];
  codeExplanation: string;
  generatedAt: Date;
}

export interface AlgorithmState {
  steps: AlgorithmStep[];
  confirmed: boolean;
  isProcessing: boolean;
  generatedCode: string | null;
  codeGenerationResult: CodeGenerationResult | null;
  executionResult: ExecutionResult | null;
  isExecuting: boolean;
  explanation: ExplanationState | null;
  chatMessages: ChatMessage[];
  isChatLoading: boolean;
}

const initialState: AlgorithmState = {
  steps: [],
  confirmed: false,
  isProcessing: false,
  generatedCode: null,
  codeGenerationResult: null,
  executionResult: null,
  isExecuting: false,
  explanation: null,
  chatMessages: [],
  isChatLoading: false
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
      update(state => ({ ...state, isExecuting })),
    
    /** Set explanation state */
    setExplanation: (explanation: ExplanationState | null) =>
      update(state => ({ ...state, explanation })),
    
    /** Add a chat message to history */
    addChatMessage: (message: ChatMessage) =>
      update(state => ({ ...state, chatMessages: [...state.chatMessages, message] })),
    
    /** Set chat loading state */
    setChatLoading: (isLoading: boolean) =>
      update(state => ({ ...state, isChatLoading: isLoading })),
    
    /** Clear chat history */
    clearChat: () =>
      update(state => ({ ...state, chatMessages: [], isChatLoading: false }))
  };
}

export const algorithmStore = createAlgorithmStore();
