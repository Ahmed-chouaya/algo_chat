/**
 * Store for algorithm step state and confirmation tracking.
 * 
 * Manages the extracted steps, confirmation status, and processing state.
 */
import { writable } from 'svelte/store';
import type { AlgorithmStep } from '$lib/processing';

export interface AlgorithmState {
  steps: AlgorithmStep[];
  confirmed: boolean;
  isProcessing: boolean;
}

const initialState: AlgorithmState = {
  steps: [],
  confirmed: false,
  isProcessing: false
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
      update(state => ({ ...state, isProcessing }))
  };
}

export const algorithmStore = createAlgorithmStore();
