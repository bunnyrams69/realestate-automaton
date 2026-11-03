"""
OpenRouter API Client
Provides asynchronous access to LLMs via OpenRouter with structured validation,
configurable models/providers, timeout handling, and resilient fallbacks.
"""

import json
import re
from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel, Field, ValidationError
from app.config.settings import settings
from app.core.exceptions import AIIntegrationException
from app.core.logging import logger


class ExtractedCustomerPreferences(BaseModel):
    """Pydantic schema for structured real estate customer requirements."""
    preferred_location: Optional[str] = None
    property_type: Optional[str] = None
    bedroom_preference: Optional[int] = None
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    purchase_timeline: Optional[str] = None
    purchase_purpose: Optional[str] = None  # Self-use, Investment
    funding_method: Optional[str] = None    # Self-funded, Home loan, Both
    site_visit_interest: Optional[bool] = None
    email: Optional[str] = None
    customer_name: Optional[str] = None


class OpenRouterClient:
    """Asynchronous client for interacting with LLM models hosted via OpenRouter."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        default_model: Optional[str] = None,
        timeout_seconds: float = 45.0,
    ):
        self.api_key = api_key or settings.OPENROUTER_API_KEY
        self.base_url = (base_url or settings.OPENROUTER_BASE_URL).rstrip("/")
        self.default_model = default_model or settings.OPENROUTER_MODEL
        self.fast_model = settings.OPENROUTER_FAST_MODEL
        self.timeout_seconds = timeout_seconds

    async def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
        response_format: Optional[Dict[str, Any]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Send a chat completion request to OpenRouter with configurable model, tools, and timeout.
        """
        if not self.api_key:
            raise AIIntegrationException("OpenRouter API key is not configured.")

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://realestate-ai.local",
            "X-Title": "Real Estate AI Sales Automation",
            "Content-Type": "application/json",
        }

        payload: Dict[str, Any] = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if response_format:
            payload["response_format"] = response_format

        if tools:
            payload["tools"] = tools

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code != 200:
                    logger.error(f"OpenRouter API error [{response.status_code}]: {response.text}")
                    raise AIIntegrationException(
                        f"OpenRouter returned status {response.status_code}: {response.text}"
                    )
                return response.json()

            except httpx.TimeoutException as exc:
                logger.error(f"OpenRouter request timed out after {self.timeout_seconds}s: {exc}")
                raise AIIntegrationException(f"OpenRouter timeout after {self.timeout_seconds}s: {exc}")
            except httpx.RequestError as exc:
                logger.error(f"OpenRouter connection exception: {exc}")
                raise AIIntegrationException(f"Failed to connect to OpenRouter: {exc}")

    async def extract_preferences(
        self,
        customer_message: str,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Extract structured customer preferences with schema validation.
        Cleans markdown wrappers and validates with Pydantic.
        """
        system_prompt = (
            "You are an expert real estate data extraction assistant for Prestige Realty. "
            "Analyze the customer's message and extract their real estate requirements into JSON format. "
            "Extract: preferred_location (string or null), property_type (APARTMENT, VILLA, PLOT, PENTHOUSE, or null), "
            "bedroom_preference (integer or null, e.g. 2 for 2BHK), budget_max (integer in INR or null, e.g. 1.5 Cr = 15000000), "
            "budget_min (integer in INR or null), purchase_timeline (string or null, e.g. 'immediate', 'within 3 months', 'just exploring'), "
            "purchase_purpose (string or null, 'Self-use' or 'Investment'), "
            "funding_method (string or null, 'Self-funded', 'Home loan', or 'Both'), "
            "site_visit_interest (boolean or null), email (string or null), "
            "and customer_name (string or null). "
            "Return ONLY valid JSON matching this schema."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Customer Message: {customer_message}"},
        ]

        try:
            response = await self.chat_completion(
                messages=messages,
                model=model or self.fast_model or self.default_model,
                temperature=0.0,
                response_format={"type": "json_object"},
            )
            msg_obj = response.get("choices", [{}])[0].get("message", {})
            content = (msg_obj.get("content") or "").strip()
            if not content:
                logger.warning("Empty content from preference extraction LLM call.")
                return {}

            # Clean any markdown code blocks
            clean_json = re.sub(r"^```(?:json)?\s*|\s*```$", "", content, flags=re.MULTILINE).strip()
            raw_dict = json.loads(clean_json)

            # Validate against Pydantic schema
            validated = ExtractedCustomerPreferences.model_validate(raw_dict)
            return validated.model_dump(exclude_none=True)

        except (AIIntegrationException, json.JSONDecodeError, ValidationError) as e:
            logger.warning(f"Structured preference extraction failed or returned malformed data: {e}")
            return {}

    async def generate_response(
        self,
        messages: Optional[List[Dict[str, str]]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        matched_properties_summary: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 600,
    ) -> str:
        """
        Generate a warm, consultative sales assistant response for WhatsApp.
        Accepts either pre-assembled messages list or conversation history.
        """
        if messages:
            prompt_messages = messages
        else:
            system_instruction = (
                "You are an intelligent, empathetic, and professional real estate sales assistant on WhatsApp. "
                "Your role is to help prospective buyers find their dream property, answer questions about locations "
                "and amenities, and coordinate on-site property walkthroughs. "
                "Rules:\n"
                "1. Be concise, polite, and conversational (keep WhatsApp messages under 3 short paragraphs).\n"
                "2. Never hallucinate property prices or features. Rely strictly on verified property details provided.\n"
                "3. If property matches are provided, present the top options clearly with their key highlights.\n"
                "4. Gently guide high-intent buyers toward scheduling an on-site visit."
            )

            prompt_messages = [{"role": "system", "content": system_instruction}]

            if matched_properties_summary:
                prompt_messages.append({
                    "role": "system",
                    "content": f"Active verified properties currently available:\n{matched_properties_summary}",
                })

            if conversation_history:
                prompt_messages.extend(conversation_history)

        result = await self.chat_completion(
            messages=prompt_messages,
            model=model or self.default_model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        msg_obj = result.get("choices", [{}])[0].get("message", {})
        content = msg_obj.get("content")
        if not content and "reasoning" in msg_obj:
            content = msg_obj.get("reasoning")
        return (content or "").strip()

    async def chat(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Tool-calling completion interface conforming to LLM Protocol.
        Returns the assistant message dict containing 'content' and/or 'tool_calls'.
        """
        result = await self.chat_completion(
            messages=messages,
            tools=tools,
            temperature=0.2,
        )
        msg = result.get("choices", [{}])[0].get("message", {})
        return msg


# Global default client instance
openrouter_client = OpenRouterClient()
