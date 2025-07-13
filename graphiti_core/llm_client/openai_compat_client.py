"""
Copyright 2024, Zep Software, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import json
import typing

from pydantic import BaseModel

from ..prompts.models import Message
from .client import MULTILINGUAL_EXTRACTION_RESPONSES
from .config import ModelSize
from .openai_generic_client import OpenAIGenericClient


class OpenAICompatClient(OpenAIGenericClient):
    """
    OpenAI API 兼容客户端，支持 DeepSeek 等兼容 OpenAI API 的大模型

    主要差异：修改 JSON 响应提示词格式，避免某些模型直接返回模板内容
    """

    async def generate_response(
        self,
        messages: list[Message],
        response_model: type[BaseModel] | None = None,
        max_tokens: int | None = None,
        model_size: ModelSize = ModelSize.medium,
    ) -> dict[str, typing.Any]:
        if max_tokens is None:
            max_tokens = self.max_tokens

        retry_count = 0
        last_error = None

        if response_model is not None:
            serialized_model = json.dumps(response_model.model_json_schema())
            # 关键差异：修改提示词格式，避免LLM返回JSON schema
            json_instruction=f"\n\nRespond with a JSON object that follows the JSON schema instruction:\n\n{serialized_model}\n\nIMPORTANT: The output JSON object should not be the instruction itself. Instead, the instruction describes the structure of the JSON object that you must generate with actual data."
            messages[-1].content += json_instruction

        # 添加多语言提取指令
        messages[0].content += MULTILINGUAL_EXTRACTION_RESPONSES

        # 调试：打印发送给LLM的完整消息
        import logging
        logger = logging.getLogger(__name__)
        logger.info("🔍 Sending messages to LLM (OpenAICompatClient):")
        for i, msg in enumerate(messages):
            logger.info(f"  Message {i+1} ({msg.role}): {msg.content[:500]}...")
            if len(msg.content) > 500:
                logger.info(f"    [Message truncated, full length: {len(msg.content)} chars]")
                # 打印消息的最后500个字符，查看我们的优化提示词
                logger.info(f"    Message {i+1} ending: ...{msg.content[-500:]}")

        # 重试逻辑（完全覆写，避免父类重新添加原来的提示词格式）
        while retry_count <= self.MAX_RETRIES:
            try:
                response = await self._generate_response(
                    messages, response_model, max_tokens=max_tokens, model_size=model_size
                )
                logger.info(f"🤖 LLM Response (OpenAICompatClient): {response}")
                return response
            except Exception as e:
                last_error = e

                # Don't retry if we've hit the max retries
                if retry_count >= self.MAX_RETRIES:
                    logger.error(f'Max retries ({self.MAX_RETRIES}) exceeded. Last error: {e}')
                    raise

                retry_count += 1

                # Construct a detailed error message for the LLM
                error_context = (
                    f'The previous response attempt was invalid. '
                    f'Error type: {e.__class__.__name__}. '
                    f'Error details: {str(e)}. '
                    f'Please try again with a valid response, ensuring the output matches '
                    f'the expected format and constraints.'
                )

                error_message = Message(role='user', content=error_context)
                messages.append(error_message)
                logger.warning(
                    f'Retrying after application error (attempt {retry_count}/{self.MAX_RETRIES}): {e}'
                )

        # If we somehow get here, raise the last error
        raise last_error or Exception('Max retries exceeded with no specific error')
