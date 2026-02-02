"""Tests for LLM service."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from langchain.schema import LLMResult, Generation

from app.services.llm_service import LLMService


class TestLLMService:
    """Tests for LLM service."""

    @pytest.mark.asyncio
    @patch('app.services.llm_service.ChatOpenAI')
    async def test_initialize_openai_provider(self, mock_chat_openai):
        """Test initialization with OpenAI provider."""
        with patch('app.services.llm_service.settings') as mock_settings:
            mock_settings.default_llm_provider = "openai"
            mock_settings.openai_api_key = "test-key"

            service = LLMService()

            assert service.provider == "openai"
            mock_chat_openai.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.services.llm_service.ChatAnthropic')
    async def test_initialize_anthropic_provider(self, mock_chat_anthropic):
        """Test initialization with Anthropic provider."""
        with patch('app.services.llm_service.settings') as mock_settings:
            mock_settings.default_llm_provider = "anthropic"
            mock_settings.anthropic_api_key = "test-key"

            service = LLMService()

            assert service.provider == "anthropic"
            mock_chat_anthropic.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_missing_api_key(self):
        """Test initialization fails with missing API key."""
        with patch('app.services.llm_service.settings') as mock_settings:
            mock_settings.default_llm_provider = "openai"
            mock_settings.openai_api_key = None

            with pytest.raises(ValueError, match="OpenAI API key not configured"):
                LLMService()

    @pytest.mark.asyncio
    async def test_initialize_unsupported_provider(self):
        """Test initialization fails with unsupported provider."""
        with patch('app.services.llm_service.settings') as mock_settings:
            mock_settings.default_llm_provider = "unsupported"

            with pytest.raises(ValueError, match="Unsupported LLM provider"):
                LLMService()

    @pytest.mark.asyncio
    @patch('app.services.llm_service.ChatOpenAI')
    @patch('app.services.llm_service.LLMChain')
    async def test_analyze_market_success(self, mock_chain_class, mock_chat_openai):
        """Test successful market analysis."""
        with patch('app.services.llm_service.settings') as mock_settings:
            mock_settings.default_llm_provider = "openai"
            mock_settings.openai_api_key = "test-key"

            # Mock LLMChain response
            mock_chain = AsyncMock()
            mock_chain.ainvoke.return_value = {
                "text": "Анализ рынка: Целевой рынок имеет высокий потенциал..."
            }
            mock_chain_class.return_value = mock_chain

            service = LLMService()
            result = await service.analyze_market(
                product_description="Мобильное приложение для доставки еды",
                industry="Общественное питание",
                region="Москва"
            )

            assert "Анализ рынка" in result
            mock_chain.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.services.llm_service.ChatOpenAI')
    @patch('app.services.llm_service.LLMChain')
    async def test_analyze_market_failure(self, mock_chain_class, mock_chat_openai):
        """Test market analysis failure."""
        with patch('app.services.llm_service.settings') as mock_settings:
            mock_settings.default_llm_provider = "openai"
            mock_settings.openai_api_key = "test-key"

            # Mock LLMChain to raise exception
            mock_chain = AsyncMock()
            mock_chain.ainvoke.side_effect = Exception("API error")
            mock_chain_class.return_value = mock_chain

            service = LLMService()

            with pytest.raises(Exception, match="LLM analysis failed"):
                await service.analyze_market(
                    product_description="Test product",
                    industry="Test industry",
                    region="Test region"
                )

    @pytest.mark.asyncio
    @patch('app.services.llm_service.ChatOpenAI')
    @patch('app.services.llm_service.LLMChain')
    async def test_generate_report_section_success(self, mock_chain_class, mock_chat_openai):
        """Test successful report section generation."""
        with patch('app.services.llm_service.settings') as mock_settings:
            mock_settings.default_llm_provider = "openai"
            mock_settings.openai_api_key = "test-key"

            # Mock LLMChain response
            mock_chain = AsyncMock()
            mock_chain.ainvoke.return_value = {
                "text": "1. ВВЕДЕНИЕ\n\nДанное исследование проводится с целью..."
            }
            mock_chain_class.return_value = mock_chain

            service = LLMService()
            result = await service.generate_report_section(
                section_type="ВВЕДЕНИЕ",
                data={"purpose": "Анализ рынка", "scope": "Регион Москва"}
            )

            assert "ВВЕДЕНИЕ" in result
            mock_chain.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.services.llm_service.ChatOpenAI')
    @patch('app.services.llm_service.LLMChain')
    async def test_generate_report_section_failure(self, mock_chain_class, mock_chat_openai):
        """Test report section generation failure."""
        with patch('app.services.llm_service.settings') as mock_settings:
            mock_settings.default_llm_provider = "openai"
            mock_settings.openai_api_key = "test-key"

            # Mock LLMChain to raise exception
            mock_chain = AsyncMock()
            mock_chain.ainvoke.side_effect = Exception("Generation error")
            mock_chain_class.return_value = mock_chain

            service = LLMService()

            with pytest.raises(Exception, match="Report generation failed"):
                await service.generate_report_section(
                    section_type="ВВЕДЕНИЕ",
                    data={}
                )
