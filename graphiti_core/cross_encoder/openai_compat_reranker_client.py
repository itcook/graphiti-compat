"""
兼容版本的 OpenAI Reranker 客户端
支持分离的 LLM 配置和环境变量
"""

import logging
import os
from typing import Any

import numpy as np
import openai
from openai import AsyncOpenAI

from ..helpers import semaphore_gather
from ..llm_client import LLMConfig, RateLimitError
from ..prompts import Message
from .client import CrossEncoderClient

logger = logging.getLogger(__name__)

class OpenAICompatRerankerClient(CrossEncoderClient):
    def __init__(self, config: LLMConfig | None = None):
        """
        Initialize the OpenAICompatRerankerClient with LLM configuration.

        Args:
            config (LLMConfig | None): LLM configuration. If None, creates from environment variables.
        """
        if config is None:
            # Use environment variables with the compatible version
            config = LLMConfig(
                api_key=os.environ.get('LLM_API_KEY'),
                base_url=os.environ.get('LLM_BASE_URL'),
                model=os.environ.get('LLM_MODEL_NAME'),
            )

        self.config = config
        self.client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )

    async def rank(self, query: str, passages: list[str]) -> list[tuple[str, float]]:
        # Same implementation logic as the original version
        openai_messages_list: Any = [
            [
                Message(
                    role='system',
                    content='You are an expert tasked with determining whether the passage is relevant to the query',
                ),
                Message(
                    role='user',
                    content=f"""
                           Respond with "True" if PASSAGE is relevant to QUERY and "False" otherwise.
                           <PASSAGE>
                           {passage}
                           </PASSAGE>
                           <QUERY>
                           {query}
                           </QUERY>
                           """,
                ),
            ]
            for passage in passages
        ]

        try:
            responses = await semaphore_gather(
                *[
                    self.client.chat.completions.create(
                        model=self.config.model,
                        messages=openai_messages,
                        temperature=0,
                        max_tokens=1,
                        logit_bias={'6432': 1, '7983': 1},
                        logprobs=True,
                        top_logprobs=2,
                    )
                    for openai_messages in openai_messages_list
                ]
            )

            responses_top_logprobs = [
                response.choices[0].logprobs.content[0].top_logprobs
                if response.choices[0].logprobs is not None
                and response.choices[0].logprobs.content is not None
                else []
                for response in responses
            ]
            scores: list[float] = []
            for top_logprobs in responses_top_logprobs:
                if len(top_logprobs) == 0:
                    continue
                norm_logprobs = np.exp(top_logprobs[0].logprob)
                if top_logprobs[0].token.strip().split(' ')[0].lower() == 'true':
                    scores.append(norm_logprobs)
                else:
                    scores.append(1 - norm_logprobs)

            results = [(passage, score) for passage, score in zip(passages, scores, strict=True)]
            results.sort(reverse=True, key=lambda x: x[1])
            return results
        except openai.RateLimitError as e:
            raise RateLimitError from e
        except Exception as e:
            logger.error(f'Error in generating LLM response: {e}')
            raise
