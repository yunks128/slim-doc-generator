"""
AI enhancement functionality for documentation content.
"""
import logging
import os
import sys
from typing import Dict, Optional


class AIEnhancer:
    """
    Enhances documentation content using AI.
    """
    
    def __init__(self, model: str, logger: logging.Logger):
        """
        Initialize the AI enhancer.
        
        Args:
            model: AI model to use in format "provider/model_name"
            logger: Logger instance
        """
        self.model = model
        self.logger = logger
        
        # Parse provider and model name
        try:
            self.provider, self.model_name = model.split('/')
        except ValueError:
            self.logger.warning(f"Invalid model format: {model}. Expected format: 'provider/model_name'")
            self.provider = "openai"  # Default provider
            self.model_name = model
        
        # Validate provider
        if self.provider not in {"openai", "azure", "ollama"}:
            self.logger.warning(f"Unsupported provider: {self.provider}. Falling back to openai.")
            self.provider = "openai"
        
        self.logger.info(f"Initialized AI enhancer with {self.provider}/{self.model_name}")
    
    def enhance(self, content: str, section_name: str) -> str:
        """
        Enhance documentation content using AI.
        
        Args:
            content: Original content to enhance
            section_name: Name of the section being enhanced
            
        Returns:
            Enhanced content
        """
        try:
            self.logger.info(f"Enhancing {section_name} content with AI")
            
            # Get enhancement prompt for the section
            prompt = self._get_enhancement_prompt(content, section_name)
            
            # Generate enhanced content using selected provider/model
            if self.provider == "openai":
                enhanced_content = self._enhance_with_openai(prompt)
            elif self.provider == "azure":
                enhanced_content = self._enhance_with_azure(prompt)
            elif self.provider == "ollama":
                enhanced_content = self._enhance_with_ollama(prompt)
            else:
                self.logger.warning(f"Unsupported provider: {self.provider}")
                return content
            
            # If enhancement failed, return original content
            if not enhanced_content:
                self.logger.warning(f"AI enhancement failed. Using original content for {section_name}.")
                return content
            
            return enhanced_content
            
        except Exception as e:
            self.logger.error(f"Error during AI enhancement: {str(e)}")
            return content  # Return original content if enhancement fails
    
    def _get_enhancement_prompt(self, content: str, section_name: str) -> str:
        """
        Get the enhancement prompt for a specific section.
        
        Args:
            content: Original content to enhance
            section_name: Name of the section being enhanced
            
        Returns:
            Enhancement prompt
        """
        prompt_templates = {
            "overview": "Enhance this project overview to be more comprehensive and user-friendly "
                      "while maintaining accuracy. Add clear sections for features, use cases, and key "
                      "concepts if they're not already present: ",
            
            "installation": "Improve this installation guide by adding clear prerequisites, "
                          "troubleshooting tips, and platform-specific instructions while "
                          "maintaining accuracy: ",
            
            "api": "Enhance this API documentation by adding more detailed descriptions, usage "
                  "examples, and parameter explanations while maintaining technical accuracy: ",
            
            "development": "Improve this development guide by adding more context, best practices, "
                         "and workflow descriptions while maintaining accuracy: ",
            
            "contributing": "Enhance these contributing guidelines by adding more specific examples, "
                          "workflow descriptions, and best practices while maintaining accuracy: "
        }
        
        # Get specific prompt for the section, or use a generic one
        prompt = prompt_templates.get(
            section_name, 
            "Enhance this documentation while maintaining accuracy and improving clarity: "
        )
        
        # Add system context to the prompt
        system_context = (
            "You are a technical documentation specialist helping to improve software documentation. "
            "Your job is to enhance the provided documentation while maintaining factual accuracy. "
            "Improve clarity, organization, and comprehensiveness. "
            "Add examples where helpful. Format using markdown."
        )
        
        # Return full prompt
        return f"{system_context}\n\n{prompt}\n\n{content}"
    
    def _enhance_with_openai(self, prompt: str) -> Optional[str]:
        """
        Enhance content using OpenAI API.
        
        Args:
            prompt: Enhancement prompt
            
        Returns:
            Enhanced content or None if enhancement failed
        """
        try:
            self.logger.debug("Using OpenAI for enhancement")
            
            # Try to import OpenAI
            try:
                from openai import OpenAI
            except ImportError:
                self.logger.error("OpenAI package not installed. Install with: pip install openai")
                return None
            
            # Check for API key
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                self.logger.error("OPENAI_API_KEY environment variable not set")
                return None
            
            # Initialize client
            client = OpenAI(api_key=api_key)
            
            # Make API call
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4096
            )
            
            # Extract and return content
            if response.choices and response.choices[0].message:
                return response.choices[0].message.content
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error using OpenAI: {str(e)}")
            return None
    
    def _enhance_with_azure(self, prompt: str) -> Optional[str]:
        """
        Enhance content using Azure OpenAI API.
        
        Args:
            prompt: Enhancement prompt
            
        Returns:
            Enhanced content or None if enhancement failed
        """
        try:
            self.logger.debug("Using Azure OpenAI for enhancement")
            
            # Try to import required packages
            try:
                from azure.identity import DefaultAzureCredential
                from openai import AzureOpenAI
            except ImportError:
                self.logger.error("Azure packages not installed. Install with: pip install azure-identity openai")
                return None
            
            # Check for required environment variables
            endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
            api_key = os.environ.get("AZURE_OPENAI_API_KEY")
            
            if not endpoint:
                self.logger.error("AZURE_OPENAI_ENDPOINT environment variable not set")
                return None
            
            # Initialize client
            if api_key:
                client = AzureOpenAI(
                    api_key=api_key,
                    api_version="2023-05-15",
                    azure_endpoint=endpoint
                )
            else:
                # Use default Azure credentials
                client = AzureOpenAI(
                    azure_ad_token_provider=DefaultAzureCredential(),
                    api_version="2023-05-15",
                    azure_endpoint=endpoint
                )
            
            # Make API call
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4096
            )
            
            # Extract and return content
            if response.choices and response.choices[0].message:
                return response.choices[0].message.content
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error using Azure OpenAI: {str(e)}")
            return None
    
    def _enhance_with_ollama(self, prompt: str) -> Optional[str]:
        """
        Enhance content using Ollama (local models).
        
        Args:
            prompt: Enhancement prompt
            
        Returns:
            Enhanced content or None if enhancement failed
        """
        try:
            self.logger.debug("Using Ollama for enhancement")
            
            # Try to import Ollama client
            try:
                import ollama
            except ImportError:
                # If ollama package is not available, try using subprocess
                return self._enhance_with_ollama_subprocess(prompt)
            
            # Make API call
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract and return content
            if response and "message" in response and "content" in response["message"]:
                return response["message"]["content"]
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error using Ollama: {str(e)}")
            
            # Fall back to subprocess method
            return self._enhance_with_ollama_subprocess(prompt)
    
    def _enhance_with_ollama_subprocess(self, prompt: str) -> Optional[str]:
        """
        Enhance content using Ollama via subprocess (fallback method).
        
        Args:
            prompt: Enhancement prompt
            
        Returns:
            Enhanced content or None if enhancement failed
        """
        try:
            self.logger.debug("Using Ollama via subprocess")
            
            # Check if ollama is installed
            import subprocess
            
            # Create a temporary file for the prompt
            import tempfile
            with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp:
                temp.write(prompt)
                temp_path = temp.name
            
            # Run ollama command
            try:
                result = subprocess.run(
                    ["ollama", "run", self.model_name, temp_path],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                # Clean up temp file
                os.unlink(temp_path)
                
                # Return output
                return result.stdout.strip()
                
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Ollama subprocess failed: {e}")
                
                # Clean up temp file
                os.unlink(temp_path)
                
                return None
                
        except Exception as e:
            self.logger.error(f"Error using Ollama subprocess: {str(e)}")
            return None