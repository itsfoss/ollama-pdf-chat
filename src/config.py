import os
import requests
from typing import List, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OllamaConfig:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OllamaConfig, cls).__new__(cls)
            cls._instance.base_url = None
            cls._instance.selected_model = None
            cls._instance.available_models = []
        return cls._instance
    
    def set_base_url(self, url: str) -> bool:
        """Set and validate Ollama base URL."""
        try:
            # Ensure URL ends with /
            url = url.rstrip('/') + '/'
            logger.info(f"Attempting to connect to Ollama at: {url}")
            
            # Test connection and get available models
            response = requests.get(f"{url}api/tags")
            if response.status_code == 200:
                self.base_url = url
                # Update available models immediately
                self.available_models = self._parse_models_from_response(response.json())
                # Set default model if none selected
                if not self.selected_model and self.available_models:
                    self.selected_model = self.available_models[0]
                logger.info(f"Connected to Ollama. Found models: {self.available_models}")
                return True
            
            logger.error(f"Failed to connect to Ollama. Status code: {response.status_code}")
            return False
            
        except Exception as e:
            logger.error(f"Error connecting to Ollama: {str(e)}")
            return False

    def _parse_models_from_response(self, response_data: dict) -> List[str]:
        """Parse models from Ollama API response."""
        try:
            # Extract model names from the response
            models = [model['name'] for model in response_data.get('models', [])]
            return sorted(models) if models else []
        except Exception as e:
            logger.error(f"Error parsing models: {str(e)}")
            return []
    
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        if not self.base_url:
            logger.warning("No base URL configured")
            return []
        
        try:
            response = requests.get(f"{self.base_url}api/tags")
            if response.status_code == 200:
                self.available_models = self._parse_models_from_response(response.json())
                return self.available_models
        except Exception as e:
            logger.error(f"Error fetching models: {str(e)}")
        
        return self.available_models

    def set_selected_model(self, model: str) -> bool:
        """Set the selected model."""
        if model in self.get_available_models():
            self.selected_model = model
            logger.info(f"Selected model: {model}")
            return True
        logger.error(f"Model {model} not available")
        return False

    def get_selected_model(self) -> Optional[str]:
        """Get the currently selected model."""
        if not self.selected_model:
            models = self.get_available_models()
            if models:
                self.selected_model = models[0]
        return self.selected_model

    def get_base_url(self) -> Optional[str]:
        """Get the base URL."""
        return self.base_url

    def is_configured(self) -> bool:
        """Check if Ollama is properly configured."""
        return bool(self.base_url and self.selected_model)
