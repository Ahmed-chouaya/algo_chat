import { invoke } from '$lib/tauri-helper';
import type { AlgorithmStep } from '$lib/processing';
import type { ChatMessage } from './stores/algorithm';

export type Provider = 'nvidia' | 'openai' | 'anthropic';

export async function setApiKey(provider: Provider, apiKey: string): Promise<void> {
  return invoke('set_api_key', { provider, apiKey });
}

export async function getApiKey(provider: Provider): Promise<string> {
  return invoke('get_api_key', { provider });
}

export async function deleteApiKey(provider: Provider): Promise<void> {
  return invoke('delete_api_key', { provider });
}

export async function getProviders(): Promise<string[]> {
  return invoke('get_all_providers');
}

/** Explanation for a single step */
export interface StepExplanation {
  stepNumber: number;
  explanation: string;
}

/** Explanation state for an algorithm */
export interface ExplanationState {
  summary: string;
  stepExplanations: StepExplanation[];
  codeExplanation: string;
  generatedAt: Date;
}

/**
 * Generate explanation for algorithm steps and code using LLM.
 * 
 * @param steps - List of algorithm steps
 * @param generatedCode - Optional generated Python code
 * @param provider - LLM provider to use
 * @returns ExplanationState with summary, step explanations, and code explanation
 */
export async function generateExplanation(
  steps: AlgorithmStep[],
  generatedCode: string | null,
  provider: Provider
): Promise<ExplanationState> {
  const stepsJson = JSON.stringify({ steps });
  const code = generatedCode || null;
  
  const result = await invoke<{
    summary: string;
    stepExplanations: StepExplanation[];
    codeExplanation: string;
    generatedAt: string;
  }>('generate_explanation', {
    stepsJson,
    code,
    provider,
  });

  return {
    summary: result.summary,
    stepExplanations: result.stepExplanations,
    codeExplanation: result.codeExplanation,
    generatedAt: new Date(result.generatedAt),
  };
}

/** Context for chat follow-up questions */
export interface ChatContext {
  algorithmSummary: string;
  steps: AlgorithmStep[];
  codeExplanation: string;
  generatedCode: string | null;
}

/**
 * Ask a follow-up question about the algorithm or code.
 * 
 * @param question - User's follow-up question
 * @param context - Algorithm context (summary, steps, code explanation)
 * @param history - Previous chat messages for context
 * @returns Assistant's response to the question
 */
export async function chatAboutExplanation(
  question: string,
  context: ChatContext,
  history: ChatMessage[]
): Promise<string> {
  // Build a prompt that includes context and history
  const stepsJson = JSON.stringify({ steps: context.steps });
  
  const result = await invoke<string>('chat_about_explanation', {
    question,
    algorithmSummary: context.algorithmSummary,
    stepsJson,
    codeExplanation: context.codeExplanation,
    generatedCode: context.generatedCode,
    historyJson: JSON.stringify({ messages: history })
  });
  
  return result;
}