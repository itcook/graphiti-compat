import logging
import typing
from typing import Any, ClassVar

import instructor
from openai import AsyncOpenAI
from pydantic import BaseModel

from ..prompts.models import Message
from .client import MULTILINGUAL_EXTRACTION_RESPONSES, LLMClient
from .config import DEFAULT_MAX_TOKENS, LLMConfig, ModelSize
from .errors import RateLimitError, RefusalError

logger = logging.getLogger(__name__)


class OpenAICompatClient(LLMClient):
    """
    OpenAI API compatible client based on instructor library

    Solves LLM JSON standardized output issues:
    - Automatic conversion from Pydantic models to structured output
    - Built-in retry and validation mechanisms
    - Support for complex nested structures
    - Better error handling and debugging information
    """

    # Maintain compatibility with other clients
    MAX_RETRIES: ClassVar[int] = 2

    def __init__(
        self,
        config: LLMConfig | None = None,
        cache: bool = False,
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ):
        if cache:
            raise NotImplementedError('Caching is not implemented for OpenAICompatClient')

        if config is None:
            config = LLMConfig()

        super().__init__(config, cache)
        self.max_tokens = max_tokens

        # Create OpenAI client
        openai_client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )

        # Wrap client with instructor, without specifying mode parameter
        # Since our target is non-GPT/Claude/Gemini LLMs, let instructor automatically choose the most suitable mode
        self.client = instructor.from_openai(openai_client)

    def _convert_messages(self, messages: list[Message]) -> list[dict[str, Any]]:
        """Convert internal Message format to OpenAI format"""
        return [
            {
                "role": message.role,
                "content": message.content
            }
            for message in messages
        ]

    async def _generate_response(
        self,
        messages: list[Message],
        response_model: type[BaseModel] | None = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        model_size: ModelSize = ModelSize.medium,
    ) -> dict[str, typing.Any]:
        """Generate structured response using instructor"""
        try:
            # Add multilingual support prompt
            messages[0].content += MULTILINGUAL_EXTRACTION_RESPONSES

            # Convert message format
            openai_messages = self._convert_messages(messages)

            # Cause some LLM will occasionally fails with default max_tokens and don't know why
            # use the 'safe_max_tokens' to avoid this issue
            safe_max_tokens = min(max_tokens, 8192)

            # Debug logging
            logger.info("🔍 Sending messages to LLM (OpenAICompatClient with Instructor):")
            
            # cloud enable this logger for logging the input messages if you need
            # for i, msg in enumerate(openai_messages):
            #     content = msg["content"]
            #     logger.info(f"  Message {i+1} ({msg['role']}): {content[:500]}...")
            #     if len(content) > 500:
            #         logger.info(f"    [Message truncated, full length: {len(content)} chars]")

            if response_model is not None:
                # Use instructor's response_model parameter
                logger.info(f"🎯 Using response_model: {response_model.__name__}")
                logger.info(f"🔧 Using safe_max_tokens: {safe_max_tokens} (original: {max_tokens})")
                response = await self.client.chat.completions.create(
                    model=self.config.model,
                    messages=openai_messages,
                    response_model=response_model,
                    max_tokens=safe_max_tokens,
                    temperature=self.config.temperature,
                )
                # instructor directly returns Pydantic object, convert to dictionary
                result = response.model_dump()
                logger.info(f"✅ Structured Responded")
                
                # cloud enable this logger for logging the output messages if you need
                # logger.info(f"✅ Structured Response: {result}")
                return result
            else:
                # Use regular text generation when no response_model
                logger.info("📝 Using text generation mode")
                logger.info(f"🔧 Using safe_max_tokens: {safe_max_tokens} (original: {max_tokens})")
                response = await self.client.chat.completions.create(
                    model=self.config.model,
                    messages=openai_messages,
                    max_tokens=safe_max_tokens,
                    temperature=self.config.temperature,
                )
                result = {"content": response.choices[0].message.content}
                logger.info(f"📄 Text responded")
                
                # cloud enable this logger for logging the output messages if you need
                # logger.info(f"📄 Text Response: {result}")
                return result

        except instructor.exceptions.InstructorRetryException as e:
            logger.error(f'❌ Instructor retry failed: {e}')
            raise RefusalError(f"Failed to generate valid structured output: {e}")
        except Exception as e:
            logger.error(f'❌ Error in generating LLM response: {e}')
            if "rate limit" in str(e).lower():
                raise RateLimitError from e
            raise

    async def generate_response(
        self,
        messages: list[Message],
        response_model: type[BaseModel] | None = None,
        max_tokens: int | None = None,
        model_size: ModelSize = ModelSize.medium,
    ) -> dict[str, typing.Any]:
        """Public interface for generating responses"""
        if max_tokens is None:
            max_tokens = self.max_tokens

        # Directly call _generate_response, instructor has built-in retry mechanism
        return await self._generate_response(
            messages, response_model, max_tokens, model_size
        )
