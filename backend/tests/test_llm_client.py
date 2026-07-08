import pytest
from unittest.mock import Mock, patch

from app.services.llm_client import LLMClient


def test_llm_client_groq_success():
    with patch("app.services.llm_client.settings") as mock_settings:
        with patch("app.services.llm_client.Groq") as mock_groq:
            with patch("app.services.llm_client.get_http_client"):
                mock_settings.LLM_PROVIDER = "groq"
                mock_settings.GROQ_API_KEY = "test-key"
                mock_settings.GROQ_MODEL = "llama-3.1-70b-versatile"
                
                mock_client = Mock()
                mock_completion = Mock()
                mock_completion.choices = [Mock(message=Mock(content="Test response"))]
                mock_client.chat.completions.create.return_value = mock_completion
                mock_groq.return_value = mock_client
                
                llm = LLMClient()
                result = llm.generate("System prompt", "User prompt")
                
                assert result == "Test response"
                assert mock_groq.called


def test_llm_client_openai_success():
    with patch("app.services.llm_client.settings") as mock_settings:
        with patch("app.services.llm_client.OpenAI") as mock_openai:
            with patch("app.services.llm_client.get_http_client"):
                mock_settings.LLM_PROVIDER = "openai"
                mock_settings.OPENAI_API_KEY = "test-key"
                mock_settings.OPENAI_MODEL = "gpt-4o-mini"
                
                mock_client = Mock()
                mock_completion = Mock()
                mock_completion.choices = [Mock(message=Mock(content="Test response"))]
                mock_client.chat.completions.create.return_value = mock_completion
                mock_openai.return_value = mock_client
                
                llm = LLMClient()
                result = llm.generate("System prompt", "User prompt")
                
                assert result == "Test response"
                assert mock_openai.called


def test_llm_client_groq_fallback_to_openai():
    with patch("app.services.llm_client.settings") as mock_settings:
        with patch("app.services.llm_client.OpenAI") as mock_openai:
            mock_settings.LLM_PROVIDER = "groq"
            mock_settings.GROQ_API_KEY = None
            mock_settings.OPENAI_API_KEY = "openai-key"
            mock_settings.OPENAI_MODEL = "gpt-4o-mini"
            
            mock_client = Mock()
            mock_completion = Mock()
            mock_completion.choices = [Mock(message=Mock(content="Fallback response"))]
            mock_client.chat.completions.create.return_value = mock_completion
            mock_openai.return_value = mock_client
            
            llm = LLMClient()
            result = llm.generate("System prompt", "User prompt")
            
            assert result == "Fallback response"


def test_llm_client_unsupported_provider():
    with patch("app.services.llm_client.settings") as mock_settings:
        mock_settings.LLM_PROVIDER = "unsupported"
        
        llm = LLMClient()
        with pytest.raises(RuntimeError, match="Unsupported LLM provider"):
            llm.generate("System prompt", "User prompt")


def test_llm_client_no_api_key():
    with patch("app.services.llm_client.settings") as mock_settings:
        mock_settings.LLM_PROVIDER = "groq"
        mock_settings.GROQ_API_KEY = None
        mock_settings.OPENAI_API_KEY = None
        
        llm = LLMClient()
        with pytest.raises(RuntimeError, match="API_KEY is required"):
            llm.generate("System prompt", "User prompt")


def test_llm_client_empty_response():
    with patch("app.services.llm_client.settings") as mock_settings:
        with patch("app.services.llm_client.Groq") as mock_groq:
            mock_settings.LLM_PROVIDER = "groq"
            mock_settings.GROQ_API_KEY = "test-key"
            mock_settings.GROQ_MODEL = "llama-3.1-70b-versatile"
            
            mock_client = Mock()
            mock_completion = Mock()
            mock_completion.choices = [Mock(message=Mock(content=None))]
            mock_client.chat.completions.create.return_value = mock_completion
            mock_groq.return_value = mock_client
            
            llm = LLMClient()
            result = llm.generate("System prompt", "User prompt")
            
            assert result == ""
