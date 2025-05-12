"""
Enhanced Recursive Thinking Chat

This module implements the Enhanced Recursive Thinking Chat class for refining solutions
through multiple rounds of recursive thinking.
"""

import os
import time
import json
import requests
from typing import Dict, List, Any, Optional

class EnhancedRecursiveThinkingChat:
    """
    A class that implements recursive thinking patterns to refine solutions
    through multiple iterations of thinking.
    """
    
    def __init__(self, api_key: str = None, model: str = "mistralai/mistral-small-3.1-24b-instruct:free"):
        """
        Initialize the Enhanced Recursive Thinking Chat.
        
        Args:
            api_key: OpenRouter API key (defaults to environment variable OPENROUTER_API_KEY)
            model: The model to use for thinking
        """
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required. Set OPENROUTER_API_KEY environment variable or pass explicitly.")
        
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.thinking_rounds = 3
        self.thinking_history = []
    
    def _call_api(self, messages: List[Dict[str, str]]) -> Dict:
        """Make an API call to OpenRouter."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages
        }
        
        response = requests.post(self.base_url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def _generate_thinking_prompt(self, user_input: str, round_number: int, previous_thoughts: List[Dict] = None) -> List[Dict[str, str]]:
        """Generate a prompt for recursive thinking based on the round number."""
        system_message = {
            "role": "system", 
            "content": (
                "You are an expert in recursive thinking, capable of iteratively improving solutions. "
                "Each round of thinking should build upon previous rounds, diving deeper into the problem "
                "and refining the solution further. Be precise, analytical, and thorough."
            )
        }
        
        user_messages = [{"role": "user", "content": user_input}]
        
        if previous_thoughts and round_number > 1:
            for i, thought in enumerate(previous_thoughts):
                content = f"Round {i+1} Thinking: {thought['content']}"
                user_messages.append({"role": "assistant", "content": content})
            
            user_messages.append({
                "role": "user", 
                "content": (
                    f"Now proceed to Round {round_number} of thinking. Build upon your previous rounds "
                    f"to further refine the solution. Be more specific, identify any remaining issues, "
                    f"and suggest concrete improvements."
                )
            })
        
        return [system_message] + user_messages
    
    def think_and_respond(self, user_input: str, verbose: bool = True) -> Dict:
        """
        Process user input with recursive thinking to generate an improved response.
        
        Args:
            user_input: The problem or prompt from the user
            verbose: Whether to print intermediate thinking steps
            
        Returns:
            A dictionary containing the final response and thinking history
        """
        self.thinking_history = []
        
        for round_num in range(1, self.thinking_rounds + 1):
            if verbose:
                print(f"\nThinking Round {round_num}...")
            
            # Generate thinking prompt
            messages = self._generate_thinking_prompt(
                user_input, 
                round_num, 
                self.thinking_history
            )
            
            # Make API call
            start_time = time.time()
            response = self._call_api(messages)
            elapsed_time = time.time() - start_time
            
            # Extract the response content
            thought_content = response["choices"][0]["message"]["content"]
            
            # Save thinking
            self.thinking_history.append({
                "round": round_num,
                "content": thought_content,
                "time_taken": elapsed_time
            })
            
            if verbose:
                print(f"Round {round_num} Complete ({elapsed_time:.2f}s)")
                print(f"Thought: {thought_content[:150]}...")
        
        # Final response construction using all thinking rounds
        final_prompt = [
            {"role": "system", "content": "Synthesize a final, improved solution based on all your thinking rounds."},
        ]
        
        for i, thought in enumerate(self.thinking_history):
            final_prompt.append({"role": "user", "content": f"Round {i+1} Thinking: {thought['content']}"})
        
        final_prompt.append({
            "role": "user", 
            "content": (
                "Based on all previous thinking rounds, provide your final comprehensive solution. "
                "Be clear, detailed, and actionable. Format your response appropriately."
            )
        })
        
        if verbose:
            print("\nGenerating final response...")
        
        # Get final response
        final_response = self._call_api(final_prompt)
        final_content = final_response["choices"][0]["message"]["content"]
        
        return {
            "final_response": final_content,
            "thinking_history": self.thinking_history,
            "rounds": self.thinking_rounds
        }

    def refine_solution(self, solution: str, constraints: List[Dict] = None, verbose: bool = True) -> str:
        """
        Refine a solution using recursive thinking.
        
        Args:
            solution: The solution to refine
            constraints: Optional constraints to consider during refinement
            verbose: Whether to print intermediate thinking steps
            
        Returns:
            The refined solution as a string
        """
        prompt = f"Refine and improve the following solution:\n\n{solution}\n\n"
        
        if constraints:
            prompt += "Consider the following constraints:\n"
            for constraint in constraints:
                prompt += f"- {constraint['type']}: {constraint['value']}\n"
        
        result = self.think_and_respond(prompt, verbose)
        return result["final_response"]

# Example usage when run as a script
if __name__ == "__main__":
    api_key = os.environ.get("OPENROUTER_API_KEY")
    chat = EnhancedRecursiveThinkingChat(api_key=api_key)
    
    # Example prompt
    prompt = """
    Design a self-healing system to monitor and automatically fix issues in a distributed application.
    """
    
    result = chat.think_and_respond(prompt)
    print("\nFinal Response:")
    print(result["final_response"])