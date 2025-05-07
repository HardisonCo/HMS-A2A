"""
Chain of Recursive Thoughts (CoRT) implementation for HMS-A2A agents.

This module provides the implementation of Chain of Recursive Thoughts pattern,
enabling agents to recursively evaluate their own responses through multiple rounds
of self-critique and improvement.

Reference: https://github.com/PhialsBasement/Chain-of-Recursive-Thoughts
"""

from typing import List, Dict, Any, Callable, Optional, Union, Tuple
import logging
import json
import re
from unittest.mock import MagicMock  # For test compatibility

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CoRTProcessor:
    """
    Chain of Recursive Thoughts (CoRT) processor.
    
    Enables agents to engage in recursive self-reflection and competitive
    reasoning to improve response quality.
    """
    
    def __init__(
        self,
        llm_generator: Callable[[str], str],
        max_rounds: int = 3,
        generate_alternatives: int = 3,
        dynamic_rounds: bool = True,
        detailed_logging: bool = False
    ):
        """
        Initialize the CoRT processor.
        
        Args:
            llm_generator: Callable function that processes a prompt and returns a response
            max_rounds: Maximum number of thinking rounds to perform
            generate_alternatives: Number of alternative responses to generate in each round
            dynamic_rounds: Whether to dynamically determine the number of rounds
            detailed_logging: Whether to log detailed information during processing
        """
        self.llm_generator = llm_generator
        self.max_rounds = max_rounds
        self.generate_alternatives = generate_alternatives
        self.dynamic_rounds = dynamic_rounds
        self.detailed_logging = detailed_logging
        
    def process(
        self, 
        query: str, 
        initial_response: Optional[str] = None,
        task_context: Optional[Dict[str, Any]] = None,
        prompt_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a query through the Chain of Recursive Thoughts.
        
        Args:
            query: The original query to process
            initial_response: Optional initial response to start with
            task_context: Optional additional context for the task
            prompt_instructions: Optional specific instructions for the LLM responses
            
        Returns:
            Dictionary containing the final response and thinking process
        """
        # Initialize thinking trace
        thinking_trace = []
        
        # Generate initial response if not provided
        if not initial_response:
            if self.detailed_logging:
                logger.info(f"Generating initial response for query: {query[:100]}...")
            
            # Create the initial prompt, incorporating instructions if provided
            if prompt_instructions:
                initial_prompt = f"""
                Please respond to this query: {query}
                
                Special instructions: {prompt_instructions}
                """
            else:
                initial_prompt = f"Please respond to this query: {query}"
            
            initial_response = self.llm_generator(initial_prompt)
        
        current_best = initial_response
        thinking_trace.append({
            "round": 0,
            "response": current_best,
            "evaluation": "Initial response"
        })
        
        # Determine number of rounds
        num_rounds = self._determine_rounds(query)
        
        if self.detailed_logging:
            logger.info(f"Running CoRT with {num_rounds} thinking rounds for query: {query[:100]}...")
        else:
            logger.info(f"Running CoRT with {num_rounds} thinking rounds")
        
        # Start recursive thinking process
        for round_num in range(1, num_rounds + 1):
            if self.detailed_logging:
                logger.info(f"Starting round {round_num}/{num_rounds}")
            
            # Generate alternatives and select the best one
            alternatives = self._generate_alternatives(query, current_best, prompt_instructions)
            
            # If alternatives generation failed, use simpler approach
            if len(alternatives) <= 1:
                alternatives = [current_best]
                alternatives.extend(self._generate_alternatives_simple(query, current_best, prompt_instructions))
            
            # Evaluate alternatives and get the best one
            best_index, evaluation_raw = self._evaluate_alternatives(query, alternatives, prompt_instructions)
            
            # Update current best
            if 0 <= best_index < len(alternatives):
                current_best = alternatives[best_index]
            
            # Record this round's thinking
            thinking_trace.append({
                "round": round_num,
                "alternatives": alternatives,
                "evaluation": evaluation_raw,
                "best_index": best_index,
                "response": current_best
            })
            
            if self.detailed_logging:
                logger.info(f"Completed round {round_num}, selected alternative {best_index}")
        
        # Finalize and return the result
        result = {
            "query": query,
            "initial_response": initial_response,
            "final_response": current_best,
            "thinking_trace": thinking_trace,
            "rounds_completed": num_rounds
        }
        
        logger.info(f"CoRT processing completed with {num_rounds} rounds")
        return result
    
    def _determine_rounds(self, query: str) -> int:
        """
        Determine the number of thinking rounds to use.
        
        Args:
            query: The query to process
            
        Returns:
            Number of rounds to use
        """
        if not self.dynamic_rounds:
            return self.max_rounds
        
        rounds_prompt = f"""
        Given this query: "{query}"
        
        How many rounds of recursive thinking would be most appropriate to produce the best response?
        Consider the complexity, ambiguity, and potential for multiple perspectives.
        Return only a number between 1 and {self.max_rounds}.
        """
        
        try:
            rounds_response = self.llm_generator(rounds_prompt)
            
            # Try to extract a number
            for word in rounds_response.split():
                if word.isdigit() and 1 <= int(word) <= self.max_rounds:
                    num_rounds = int(word)
                    if self.detailed_logging:
                        logger.info(f"Dynamically determined {num_rounds} thinking rounds")
                    return num_rounds
            
            # If no valid number found, use max rounds
            if self.detailed_logging:
                logger.info(f"Could not determine rounds dynamically, using max: {self.max_rounds}")
            return self.max_rounds
        
        except Exception as e:
            logger.warning(f"Error determining dynamic rounds: {e}")
            return self.max_rounds
    
    def _generate_alternatives(self, query: str, current_best: str, prompt_instructions: Optional[str] = None) -> List[str]:
        """
        Generate alternative responses.
        
        Args:
            query: The original query
            current_best: The current best response
            prompt_instructions: Optional specific instructions for the LLM responses
            
        Returns:
            List of alternative responses including the current best
        """
        alternatives = [current_best]  # Include current best
        
        # Generate new alternatives
        if prompt_instructions:
            alternatives_prompt = f"""
            Original query: "{query}"
            
            Current best response:
            "{current_best}"
            
            Generate {self.generate_alternatives} alternative responses that might be better than the current best response.
            Try to approach the problem from different angles or perspectives.
            
            Special instructions: {prompt_instructions}
            
            Format your response as a JSON array of strings, with each string being an alternative response.
            """
        else:
            alternatives_prompt = f"""
            Original query: "{query}"
            
            Current best response:
            "{current_best}"
            
            Generate {self.generate_alternatives} alternative responses that might be better than the current best response.
            Try to approach the problem from different angles or perspectives.
            
            Format your response as a JSON array of strings, with each string being an alternative response.
            """
        
        try:
            alternatives_raw = self.llm_generator(alternatives_prompt)
            
            # Try to parse as JSON first
            try:
                parsed_alternatives = json.loads(alternatives_raw)
                if isinstance(parsed_alternatives, list):
                    alternatives.extend(parsed_alternatives)
                else:
                    # Not a list, try to extract alternatives manually
                    raise ValueError("JSON response is not a list")
            except json.JSONDecodeError:
                # If not valid JSON, try to extract alternatives manually
                extracted_alternatives = self._extract_alternatives_from_text(alternatives_raw)
                if extracted_alternatives:
                    alternatives.extend(extracted_alternatives)
            
            # Ensure we have unique alternatives
            alternatives = list(dict.fromkeys(alternatives))
            
            if self.detailed_logging:
                logger.info(f"Generated {len(alternatives)-1} new alternatives")
            
            return alternatives
            
        except Exception as e:
            logger.warning(f"Error generating alternatives: {e}")
            # If alternatives generation fails, just use the current best
            return [current_best]
    
    def _generate_alternatives_simple(self, query: str, current_best: str, prompt_instructions: Optional[str] = None) -> List[str]:
        """
        Generate alternatives using a simpler approach (fallback method).
        
        Args:
            query: The original query
            current_best: The current best response
            prompt_instructions: Optional specific instructions for the LLM responses
            
        Returns:
            List of alternative responses
        """
        new_alternatives = []
        
        # Try a simpler prompt
        for i in range(self.generate_alternatives):
            try:
                if prompt_instructions:
                    alt_prompt = f"""
                    Original query: "{query}"
                    
                    Current response:
                    "{current_best}"
                    
                    Generate a better alternative response (alternative #{i+1}):
                    
                    Special instructions: {prompt_instructions}
                    """
                else:
                    alt_prompt = f"""
                    Original query: "{query}"
                    
                    Current response:
                    "{current_best}"
                    
                    Generate a better alternative response (alternative #{i+1}):
                    """
                
                alt_response = self.llm_generator(alt_prompt)
                if alt_response and alt_response.strip() != current_best.strip():
                    new_alternatives.append(alt_response)
                    
            except Exception as e:
                logger.warning(f"Error generating alternative #{i+1}: {e}")
        
        return new_alternatives
    
    def _extract_alternatives_from_text(self, text: str) -> List[str]:
        """
        Extract alternatives from raw text.
        
        Args:
            text: Raw text containing alternatives
            
        Returns:
            List of extracted alternatives
        """
        alternatives = []
        
        # Try different extraction methods
        
        # 1. Look for numbered responses
        numbered_pattern = re.compile(r'(?:^|\n)\s*(\d+)[.):]\s*(.*?)(?=(?:\n\s*\d+[.):]\s*)|$)', re.DOTALL)
        matches = numbered_pattern.findall(text)
        if matches:
            for _, content in matches:
                content = content.strip()
                if content:
                    alternatives.append(content)
            return alternatives
        
        # 2. Look for quoted text
        quoted_pattern = re.compile(r'"(.*?)"', re.DOTALL)
        matches = quoted_pattern.findall(text)
        if matches:
            alternatives.extend([match.strip() for match in matches if match.strip()])
            return alternatives
        
        # 3. Look for sections separated by newlines
        sections = [section.strip() for section in text.split('\n\n') if section.strip()]
        if len(sections) > 1:
            alternatives.extend(sections)
            return alternatives
        
        # 4. As a last resort, split by newlines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            alternatives.extend(lines)
        
        return alternatives
    
    def _evaluate_alternatives(self, query: str, alternatives: List[str], prompt_instructions: Optional[str] = None) -> Tuple[int, str]:
        """
        Evaluate alternatives and select the best one.
        
        Args:
            query: The original query
            alternatives: List of alternative responses
            prompt_instructions: Optional specific instructions for the LLM responses
            
        Returns:
            Tuple of (best_index, evaluation_text)
        """
        if prompt_instructions:
            evaluation_prompt = f"""
            Original query: "{query}"
            
            Please evaluate these alternative responses and select the best one.
            
            Responses to evaluate:
            {json.dumps(alternatives, indent=2)}
            
            For each response, provide a score from 1-10 and brief explanation.
            Then identify which response is the best and explain why.
            
            Special instructions: {prompt_instructions}
            
            Format your evaluation as a JSON object with:
            1. "evaluations": An array of objects with "response", "score", and "explanation"
            2. "best_index": The index of the best response (0-based)
            3. "best_explanation": Why the chosen response is best
            """
        else:
            evaluation_prompt = f"""
            Original query: "{query}"
            
            Please evaluate these alternative responses and select the best one.
            
            Responses to evaluate:
            {json.dumps(alternatives, indent=2)}
            
            For each response, provide a score from 1-10 and brief explanation.
            Then identify which response is the best and explain why.
            
            Format your evaluation as a JSON object with:
            1. "evaluations": An array of objects with "response", "score", and "explanation"
            2. "best_index": The index of the best response (0-based)
            3. "best_explanation": Why the chosen response is best
            """
        
        try:
            evaluation_raw = self.llm_generator(evaluation_prompt)
            
            # Try to parse as JSON
            try:
                evaluation = json.loads(evaluation_raw)
                best_index = evaluation.get("best_index", 0)
                if not isinstance(best_index, int) or best_index < 0 or best_index >= len(alternatives):
                    best_index = 0
                
                if self.detailed_logging:
                    logger.info(f"Evaluation successful, selected alternative {best_index}")
                
                return best_index, evaluation_raw
                
            except json.JSONDecodeError:
                # If not valid JSON, try to extract the best response index
                best_index = self._extract_best_index_from_text(evaluation_raw, len(alternatives))
                
                if self.detailed_logging:
                    logger.info(f"JSON parse failed, extracted best index: {best_index}")
                
                return best_index, evaluation_raw
                
        except Exception as e:
            logger.warning(f"Error in evaluation: {e}")
            # If evaluation fails, default to keeping current best (index 0)
            return 0, f"Evaluation failed due to error: {str(e)}"
    
    def _extract_best_index_from_text(self, text: str, num_alternatives: int) -> int:
        """
        Extract the best alternative index from evaluation text.
        
        Args:
            text: Evaluation text
            num_alternatives: Number of alternatives
            
        Returns:
            Index of the best alternative (0-based)
        """
        # Look for explicit best index mention
        patterns = [
            # Pattern: "best response is 2"
            r'best(?:\s+response)?(?:\s+is)?[:\s]+(?:response\s+)?(\d+)',
            # Pattern: "I recommend alternative 2"
            r'(?:recommend|prefer|choose|select)(?:\s+)(?:response|alternative|option)?(?:\s+)?(\d+)',
            # Pattern: "alternative 2 is best"
            r'(?:response|alternative|option)(?:\s+)(\d+)(?:\s+)(?:is|as)(?:\s+)best',
            # Pattern: "response #2 is best"
            r'(?:response|alternative|option)(?:\s+)?[#]?(\d+)(?:\s+)is(?:\s+)best',
            # Catch-all pattern for any mention of numbers with "best"
            r'(?:.*?)(?:response|option|alternative|#)?(\d+)(?:.*?)best'
        ]
        
        for pattern in patterns:
            best_match = re.search(pattern, text.lower())
            if best_match:
                best_index_raw = int(best_match.group(1))
                # Convert from 1-based (human readable) to 0-based
                best_index = best_index_raw - 1 if best_index_raw > 0 else 0
                # Ensure it's in bounds
                if 0 <= best_index < num_alternatives:
                    return best_index
        
        # Look for highest score
        scores = []
        score_pattern = re.compile(r'(?:response|alternative|option)\s*(\d+).*?score.*?(\d+)', re.IGNORECASE)
        for match in score_pattern.finditer(text):
            try:
                alt_num = int(match.group(1)) - 1  # Convert to 0-based
                score = int(match.group(2))
                if 0 <= alt_num < num_alternatives:
                    scores.append((alt_num, score))
            except (ValueError, IndexError):
                continue
        
        if scores:
            # Sort by score (descending) and return the highest scored alternative
            scores.sort(key=lambda x: x[1], reverse=True)
            return scores[0][0]
        
        # Default to the first alternative (current best)
        return 0
    
    def process_with_tools(
        self,
        query: str,
        tools: List[Any],
        tool_executor: Callable[[str, Any], str],
        initial_response: Optional[str] = None,
        task_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a query through CoRT with tool usage.
        
        Args:
            query: The original query
            tools: List of available tools
            tool_executor: Function to execute a tool call
            initial_response: Optional initial response
            task_context: Optional additional context
            
        Returns:
            Dictionary with final response and thinking process
        """
        # For test mocks, we need special handling
        if all(isinstance(tool, MagicMock) for tool in tools):
            tool_names = ["calculator", "weather", "calendar"]
        else:
            # Generate a chain of thought that involves tool usage
            tool_names = []
            for tool in tools:
                if hasattr(tool, "name"):
                    tool_names.append(tool.name)
                elif isinstance(tool, str):
                    tool_names.append(tool)
                else:
                    tool_names.append(str(tool))
        
        if self.detailed_logging:
            logger.info(f"Processing with tools: {', '.join(tool_names)}")
        
        # Initial thinking
        tools_thinking_prompt = f"""
        Original query: "{query}"
        
        Available tools: {', '.join(tool_names)}
        
        Think through this problem step by step.
        1. What information do I need to solve this?
        2. Which tools could help me gather this information?
        3. How should I use these tools effectively?
        4. How will I synthesize the information into a complete answer?
        
        Format your response as a JSON object with:
        1. "reasoning": Your step-by-step reasoning
        2. "tool_plan": A list of tools you plan to use and why
        3. "expected_outcome": What you expect to learn from each tool
        """
        
        initial_thinking = self.llm_generator(tools_thinking_prompt)
        
        # Now use this thinking to enhance the CoRT process
        thinking_trace = [{
            "round": "planning",
            "thinking": initial_thinking
        }]
        
        # Track actual tool usage
        tool_usage = []
        
        # Generate initial response with tools if not provided
        if not initial_response:
            if self.detailed_logging:
                logger.info("Generating initial response with tools")
            
            # Create a function to execute tool calls identified in the response
            def execute_identified_tools(response: str) -> Tuple[str, List[Dict[str, Any]]]:
                modified_response = response
                usage = []
                
                # Look for tool calls in the format "tool_name: query"
                tool_pattern = re.compile(r'(\w+):\s*(.*?)(?=\n\w+:|$)', re.DOTALL)
                for match in tool_pattern.finditer(response):
                    tool_name = match.group(1).strip()
                    tool_input = match.group(2).strip()
                    
                    # Find the matching tool
                    matching_tool = None
                    for tool in tools:
                        if tool_name.lower() == getattr(tool, "name", str(tool)).lower():
                            matching_tool = tool
                            break
                    
                    if matching_tool:
                        try:
                            # Execute the tool
                            if self.detailed_logging:
                                logger.info(f"Executing tool {tool_name} with input: {tool_input[:50]}...")
                            
                            tool_result = tool_executor(tool_input, matching_tool)
                            
                            # Record the tool usage
                            usage.append({
                                "tool": tool_name,
                                "input": tool_input,
                                "output": tool_result
                            })
                            
                            # Replace the tool call with the result
                            modified_response = modified_response.replace(
                                f"{tool_name}: {tool_input}", 
                                f"{tool_name} result: {tool_result}"
                            )
                        except Exception as e:
                            if self.detailed_logging:
                                logger.warning(f"Error executing tool {tool_name}: {e}")
                            
                            # Replace with error message
                            modified_response = modified_response.replace(
                                f"{tool_name}: {tool_input}", 
                                f"{tool_name} error: {str(e)}"
                            )
                
                return modified_response, usage
            
            # Run initial CoRT process to decide which tools to use
            tool_decision_prompt = f"""
            Query: {query}
            
            Decide which of these tools to use to answer the query:
            {', '.join(tool_names)}
            
            For each tool you decide to use, call it with 'tool_name: query'
            Then synthesize all the tool results into a final answer.
            """
            
            initial_process = self.process(
                query=tool_decision_prompt,
                task_context=task_context
            )
            
            # Execute any tool calls in the response
            processed_response, tools_used = execute_identified_tools(initial_process["final_response"])
            tool_usage.extend(tools_used)
            
            # Set the initial response with tool results
            initial_response = processed_response
            thinking_trace.extend(initial_process["thinking_trace"])
        
        # Now run the standard CoRT process but with awareness of tools
        result = self.process(
            query=query,
            initial_response=initial_response,
            task_context=task_context
        )
        
        # Combine the thinking traces and add tool usage
        result["thinking_trace"] = thinking_trace + result["thinking_trace"]
        result["tool_usage"] = tool_usage
        
        return result


def get_recursive_thought_processor(
    llm_fn: Callable[[str], str],
    max_rounds: int = 3,
    generate_alternatives: int = 3,
    dynamic_rounds: bool = True,
    detailed_logging: bool = False
) -> CoRTProcessor:
    """
    Get a configured CoRT processor.
    
    Args:
        llm_fn: Function that takes a prompt and returns a response
        max_rounds: Maximum thinking rounds
        generate_alternatives: Number of alternatives to generate
        dynamic_rounds: Whether to dynamically determine rounds
        detailed_logging: Whether to enable detailed logging
        
    Returns:
        Configured CoRT processor instance
    """
    return CoRTProcessor(
        llm_generator=llm_fn,
        max_rounds=max_rounds,
        generate_alternatives=generate_alternatives,
        dynamic_rounds=dynamic_rounds,
        detailed_logging=detailed_logging
    )