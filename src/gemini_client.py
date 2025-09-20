"""Gemini API client for generating AI-powered bug fixes and code suggestions."""

import google.generativeai as genai
from typing import List, Dict, Any, Optional

from config import GEMINI_API_KEY


class GeminiClient:
    """Client for interacting with Google's Gemini API."""
    
    def __init__(self, api_key: str = None):
        """Initialize the Gemini client."""
        self.api_key = api_key or GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable.")
        
        # Configure the API
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def generate_bug_fix(self, error_message: str, error_traceback: str, 
                        relevant_code: List[Dict[str, Any]]) -> str:
        """Generate a bug fix suggestion based on error and relevant code context."""
        prompt = self._build_bug_fix_prompt(error_message, error_traceback, relevant_code)
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating bug fix with Gemini: {e}")
            return f"Error generating fix: {str(e)}"
    
    def suggest_code_improvement(self, code_chunk: str, context: str = "") -> str:
        """Suggest improvements for a code chunk."""
        prompt = self._build_improvement_prompt(code_chunk, context)
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating code improvement with Gemini: {e}")
            return f"Error generating improvement: {str(e)}"
    
    def explain_code(self, code_chunk: str, specific_question: str = "") -> str:
        """Explain what a code chunk does."""
        prompt = self._build_explanation_prompt(code_chunk, specific_question)
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating code explanation with Gemini: {e}")
            return f"Error generating explanation: {str(e)}"
    
    def _build_bug_fix_prompt(self, error_message: str, error_traceback: str, 
                             relevant_code: List[Dict[str, Any]]) -> str:
        """Build a comprehensive prompt for bug fixing."""
        prompt_parts = [
            "You are an expert software engineer tasked with fixing a bug. ",
            "Analyze the error message, traceback, and relevant code context to provide a precise fix.",
            "",
            "## Error Information:",
            f"**Error Message:** {error_message}",
            "",
        ]
        
        if error_traceback:
            prompt_parts.extend([
                "**Error Traceback:**",
                "```",
                error_traceback,
                "```",
                "",
            ])
        
        prompt_parts.extend([
            "## Relevant Code Context:",
            "The following code chunks are semantically related to the error:",
            "",
        ])
        
        for i, code_info in enumerate(relevant_code, 1):
            metadata = code_info["metadata"]
            prompt_parts.extend([
                f"### Code Chunk {i}:",
                f"**File:** {metadata['file_path']}",
                f"**Type:** {metadata['chunk_type']} - {metadata['name']}",
                f"**Lines:** {metadata['start_line']}-{metadata['end_line']}",
                f"**Similarity Score:** {code_info['similarity_score']:.3f}",
                "",
                "```python",
                code_info["content"],
                "```",
                "",
            ])
            
            if metadata.get("docstring"):
                prompt_parts.extend([
                    f"**Documentation:** {metadata['docstring']}",
                    "",
                ])
        
        prompt_parts.extend([
            "## Instructions:",
            "1. Analyze the error and identify the root cause",
            "2. Examine the relevant code chunks for potential issues",
            "3. Provide a specific, actionable fix",
            "4. Explain why this fix addresses the problem",
            "5. If possible, suggest improvements to prevent similar issues",
            "",
            "## Response Format:",
            "Please structure your response as follows:",
            "",
            "**Root Cause Analysis:**",
            "[Explain what's causing the error]",
            "",
            "**Proposed Fix:**",
            "```python",
            "[Show the corrected code]",
            "```",
            "",
            "**Explanation:**",
            "[Explain why this fix works]",
            "",
            "**Additional Recommendations:**",
            "[Optional suggestions for improvement]",
        ])
        
        return "\n".join(prompt_parts)
    
    def _build_improvement_prompt(self, code_chunk: str, context: str = "") -> str:
        """Build a prompt for code improvement suggestions."""
        prompt_parts = [
            "You are an expert software engineer reviewing code for improvements. ",
            "Analyze the provided code and suggest enhancements for readability, performance, ",
            "maintainability, and best practices.",
            "",
            "## Code to Review:",
            "```python",
            code_chunk,
            "```",
            "",
        ]
        
        if context:
            prompt_parts.extend([
                "## Additional Context:",
                context,
                "",
            ])
        
        prompt_parts.extend([
            "## Instructions:",
            "1. Identify areas for improvement",
            "2. Suggest specific changes",
            "3. Explain the benefits of each suggestion",
            "4. Consider code quality, performance, and maintainability",
            "",
            "## Response Format:",
            "**Improvement Suggestions:**",
            "1. [First suggestion with explanation]",
            "2. [Second suggestion with explanation]",
            "...",
            "",
            "**Improved Code:**",
            "```python",
            "[Show the improved version]",
            "```",
        ])
        
        return "\n".join(prompt_parts)
    
    def _build_explanation_prompt(self, code_chunk: str, specific_question: str = "") -> str:
        """Build a prompt for code explanation."""
        prompt_parts = [
            "You are an expert software engineer explaining code to a colleague. ",
            "Provide a clear, comprehensive explanation of what the code does.",
            "",
            "## Code to Explain:",
            "```python",
            code_chunk,
            "```",
            "",
        ]
        
        if specific_question:
            prompt_parts.extend([
                "## Specific Question:",
                specific_question,
                "",
            ])
        
        prompt_parts.extend([
            "## Instructions:",
            "1. Explain the overall purpose of the code",
            "2. Break down key components and logic",
            "3. Highlight important patterns or techniques used",
            "4. Mention any potential issues or edge cases",
            "",
            "## Response Format:",
            "**Purpose:**",
            "[What does this code do?]",
            "",
            "**Key Components:**",
            "- [Component 1]: [Explanation]",
            "- [Component 2]: [Explanation]",
            "...",
            "",
            "**Important Notes:**",
            "[Any additional insights or considerations]",
        ])
        
        return "\n".join(prompt_parts)
    
    def generate_custom_prompt(self, custom_prompt: str) -> str:
        """Generate a response for a custom prompt."""
        try:
            response = self.model.generate_content(custom_prompt)
            return response.text
        except Exception as e:
            print(f"Error generating custom response with Gemini: {e}")
            return f"Error generating response: {str(e)}"