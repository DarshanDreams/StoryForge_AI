from abc import ABC, abstractmethod

from src.llm.models import LLMRequest, LLMResponse


class LLMProvider(ABC):

    @abstractmethod
    def generate(
        self,
        request: LLMRequest,
    ) -> LLMResponse:
        raise NotImplementedError