
## Overview
This library provides a flexible interface to interact with various LLM providers including HuggingFace, WatsonX, and Ollama through a unified API.

## Environment Setup

Create a `.env` file in your project root with the following variables (add only the ones needed for your providers):

```plaintext
# HuggingFace
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token

# WatsonX
WATSONX_API_KEY=your_watsonx_api_key
WATSONX_URL=your_watsonx_url
WATSONX_PROJECT_ID=your_watsonx_project_id
```

## Quick Start

```python
from lmabc.core import BiocatalysisAssistant

# Initialize the assistant
assistant = BiocatalysisAssistant(
    model="HuggingFaceH4/zephyr-7b-beta",  # Model name
    provider="huggingface",                 # Provider name
    use_memory=True                         # Enable conversation memory
)

# Initialize the agent
agent = assistant.initiate_agent()

# Use the agent
response = agent.invoke({"input": "your query here"})
```

## Provider Configuration

### HuggingFace Models
```python
assistant = BiocatalysisAssistant(
    model="HuggingFaceH4/zephyr-7b-beta",
    provider="huggingface",
    model_kwargs={
        "max_new_tokens": 512,
        "do_sample": False,
        "repetition_penalty": 1.03,
        "return_full_text": True
    }
)
```

### WatsonX Models
```python
assistant = BiocatalysisAssistant(
    model="meta-llama/llama-3-1-70b-instruct",
    provider="watsonx",
    model_kwargs={
        "max_new_tokens": 2048,
        "temperature": 0,
        "decoding_method": "sample"
    }
)
```

### Ollama Models
```python
assistant = BiocatalysisAssistant(
    model="llama3.2",
    provider="ollama",
    model_kwargs={
        "max_new_tokens": 512,
        "do_sample": False,
        "repetition_penalty": 1.03
    }
)
```

### Other LangChain Providers
For other providers supported by LangChain, use the standard initialization:

```python
assistant = BiocatalysisAssistant(
    model="model_name",
    provider="provider_name",
    model_kwargs={...}  # Provider-specific parameters
)
```

## Memory Management

The BiocatalysisAssistant includes conversation memory management:

```python
# Enable memory (default)
assistant = BiocatalysisAssistant(use_memory=True)

# Disable memory
assistant = BiocatalysisAssistant(use_memory=False)
```

When memory is enabled, the assistant maintains context across multiple interactions.

## Error Handling

The library includes comprehensive error handling for common issues:

```python
try:
    assistant = BiocatalysisAssistant(
        model="invalid_model",
        provider="invalid_provider"
    )
except Exception as e:
    print(f"Error initializing assistant: {e}")
```

Common errors include:
- Missing API keys
- Invalid model names
- Connection issues
- Provider-specific errors

## Best Practices

1. **API Key Management**
   - Always use environment variables for API keys
   - Never hardcode sensitive credentials
   - Use the .env file for local development

2. **Resource Management**
   - Initialize the assistant once and reuse it
   - Close connections properly when done
   - Monitor token usage for paid APIs

3. **Error Handling**
   - Always wrap initialization in try-except blocks
   - Handle provider-specific errors appropriately
   - Implement proper fallback mechanisms

## Known Limitations

- Memory management may increase token usage
- Some providers may have rate limits
- Response times vary by provider and model
- Token limits vary by model

## Troubleshooting

Common issues and solutions:

1. **Authentication Errors**
   - Verify API keys in .env file
   - Check environment variable loading
   - Ensure proper permissions for the API key

2. **Connection Issues**
   - Check internet connectivity
   - Verify API endpoint accessibility
   - Check for provider service status

3. **Performance Issues**
   - Consider using a different model
   - Adjust token limits
   - Monitor system resources

## Support and Resources

- GitHub Repository: [GT4SD/lm-assistant-for-biocatalysis](https://github.com/GT4SD/lm-assistant-for-biocatalysis)
- Issue Tracker: [GitHub Issues](https://github.com/GT4SD/lm-assistant-for-biocatalysis/issues)