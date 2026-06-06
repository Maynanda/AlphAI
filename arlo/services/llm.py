"""
Local LLM service wrapper using Hugging Face transformers.
"""

import json
import logging
from typing import Optional, Dict, Any
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

logger = logging.getLogger(__name__)

class LocalLLM:
    """
    Wrapper for local transformer model.
    """
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.tokenizer = None
        self.model = None
        self.is_loaded = False

    def load_model(self) -> bool:
        """
        Loads the tokenizer and model into memory.
        Returns True if successful, False otherwise.
        """
        try:
            logger.info(f"Loading local transformer model from: {self.model_path}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            
            # Using torch.float16 or auto depending on availability
            device_map = "auto" if torch.cuda.is_available() or torch.backends.mps.is_available() else None
            torch_dtype = torch.float16 if torch.cuda.is_available() or torch.backends.mps.is_available() else torch.float32

            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                torch_dtype=torch_dtype,
                device_map=device_map
            )
            self.is_loaded = True
            logger.info("Local LLM model loaded successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to load local LLM model: {e}")
            self.is_loaded = False
            return False

    def generate(self, system: str, user: str, max_new_tokens: int = 512) -> str:
        """
        Generates text given system and user instructions.
        """
        if not self.is_loaded or self.model is None or self.tokenizer is None:
            raise RuntimeError("LLM model is not loaded. Call load_model() first.")

        try:
            # Check if tokenizer has chat template support
            if hasattr(self.tokenizer, "apply_chat_template") and self.tokenizer.chat_template is not None:
                messages = [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ]
                prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            else:
                prompt = f"System: {system}\n\nUser: {user}\n\nAssistant:"

            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    pad_token_id=self.tokenizer.eos_token_id
                )

            # Strip prompt from outputs
            generated_ids = outputs[0][inputs.input_ids.shape[1]:]
            return self.tokenizer.decode(generated_ids, skip_special_tokens=True).strip()
        except Exception as e:
            logger.error(f"Error during generation: {e}")
            raise

    def generate_json(self, system: str, user: str) -> Dict[str, Any]:
        """
        Generates content and parses it as a JSON object.
        Retries once on JSON parsing failure.
        """
        system_json = f"{system}\n\nIMPORTANT: Return ONLY valid JSON. Do not include markdown formatting, code block ticks, or introductory text."
        
        try:
            response = self.generate(system_json, user)
            return self._parse_json(response)
        except json.JSONDecodeError:
            logger.warning("JSON parse failed. Retrying once with explicit request.")
            # Retry system prompt update
            retry_system = f"{system}\n\nCRITICAL: The previous output failed to parse as JSON. Please yield ONLY a valid JSON block starting with '{{' and ending with '}}'."
            response = self.generate(retry_system, user)
            return self._parse_json(response)

    def _parse_json(self, text: str) -> Dict[str, Any]:
        """Cleans and parses a JSON response string."""
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        return json.loads(cleaned)
