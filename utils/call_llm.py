from google import genai
import os
import logging
import json
from datetime import datetime

# Configure logging
log_directory = os.getenv("LOG_DIR", "logs")
os.makedirs(log_directory, exist_ok=True)
log_file = os.path.join(
    log_directory, f"llm_calls_{datetime.now().strftime('%Y%m%d')}.log"
)

# Set up logger
logger = logging.getLogger("llm_logger")
logger.setLevel(logging.INFO)
logger.propagate = False  # Prevent propagation to root logger
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logger.addHandler(file_handler)

# Simple cache configuration
cache_file = "llm_cache.json"

"""
=== LLM OPTIMIZATION GUIDE ===

CURRENT SETUP: Anthropic Claude Haiku with Extended Thinking

Configuration via Environment Variables:
  - ANTHROPIC_API_KEY:           Your API key (required)
  - ANTHROPIC_MODEL:             Model name (default: claude-haiku-4-5-20251001)
  - ANTHROPIC_MAX_TOKENS:        Max output tokens (default: 8000)
  - ANTHROPIC_THINKING_BUDGET:   Max thinking tokens (default: 5000)

OPTIMIZATION RATIONALE:
  ✓ Reduced thinking_budget from 20,000 → 5,000
    - Haiku is fast and cheap; excessive thinking is unnecessary
    - 5,000 tokens covers complex reasoning without wasting money
    
  ✓ Reduced max_tokens from 21,000 → 8,000
    - Most code/text analysis tasks need <8000 tokens
    - Reduces latency and cost
    
  ✓ Proper response parsing
    - Safely iterates content blocks instead of assuming index [1]
    - Handles edge cases (no text content, unexpected formats)
    
  ✓ Comprehensive logging
    - Logs prompts and responses for debugging
    - Truncates long text to keep logs readable
    
  ✓ Caching support restored
    - Reuses results for identical prompts
    - Saves money on repeated queries
    
  ✓ Better error handling
    - Validates API key before making calls
    - Provides clear error messages
    - Catches and logs all exceptions

RECOMMENDED SETTINGS BY USE CASE:
  Code Analysis/Review:
    - MAX_TOKENS: 6000
    - THINKING_BUDGET: 3000
    
  Documentation Generation:
    - MAX_TOKENS: 5000
    - THINKING_BUDGET: 2000
    
  Complex Reasoning:
    - MAX_TOKENS: 10000
    - THINKING_BUDGET: 8000
    
  Quick Summaries:
    - MAX_TOKENS: 3000
    - THINKING_BUDGET: 1000

Example Usage:
  export ANTHROPIC_API_KEY="your-key"
  export ANTHROPIC_MAX_TOKENS=6000
  export ANTHROPIC_THINKING_BUDGET=3000
  python main.py
"""

# By default, we Google Gemini 2.5 pro, as it shows great performance for code understanding
# def call_llm(prompt: str, use_cache: bool = True) -> str:
#     # Log the prompt
#     logger.info(f"PROMPT: {prompt}")

#     # Check cache if enabled
#     if use_cache:
#         # Load cache from disk
#         cache = {}
#         if os.path.exists(cache_file):
#             try:
#                 with open(cache_file, "r", encoding="utf-8") as f:
#                     cache = json.load(f)
#             except:
#                 logger.warning(f"Failed to load cache, starting with empty cache")

#         # Return from cache if exists
#         if prompt in cache:
#             logger.info(f"RESPONSE: {cache[prompt]}")
#             return cache[prompt]

#     # # Call the LLM if not in cache or cache disabled
#     # client = genai.Client(
#     #     vertexai=True,
#     #     # TODO: change to your own project id and location
#     #     project=os.getenv("GEMINI_PROJECT_ID", "your-project-id"),
#     #     location=os.getenv("GEMINI_LOCATION", "us-central1")
#     # )

#     # You can comment the previous line and use the AI Studio key instead:
#     # https://aistudio.google.com/api-keys
#     client = genai.Client(
#         api_key=os.getenv("GEMINI_API_KEY", ""),
#     )
#     model = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
#     # model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
#     response = client.models.generate_content(model=model, contents=[prompt])
#     response_text = response.text

#     # Log the response
#     logger.info(f"RESPONSE: {response_text}")

#     # Update cache if enabled
#     if use_cache:
#         # Load cache again to avoid overwrites
#         cache = {}
#         if os.path.exists(cache_file):
#             try:
#                 with open(cache_file, "r", encoding="utf-8") as f:
#                     cache = json.load(f)
#             except:
#                 pass

#         # Add to cache and save
#         cache[prompt] = response_text
#         try:
#             with open(cache_file, "w", encoding="utf-8") as f:
#                 json.dump(cache, f)
#         except Exception as e:
#             logger.error(f"Failed to save cache: {e}")

#     return response_text


# # Use Azure OpenAI
# def call_llm(prompt, use_cache: bool = True):
#     from openai import AzureOpenAI

#     endpoint = "https://<azure openai name>.openai.azure.com/"
#     deployment = "<deployment name>"

#     subscription_key = "<azure openai key>"
#     api_version = "<api version>"

#     client = AzureOpenAI(
#         api_version=api_version,
#         azure_endpoint=endpoint,
#         api_key=subscription_key,
#     )

#     r = client.chat.completions.create(
#         model=deployment,
#         messages=[{"role": "user", "content": prompt}],
#         response_format={
#             "type": "text"
#         },
#         max_completion_tokens=40000,
#         reasoning_effort="medium",
#         store=False
#     )
#     return r.choices[0].message.content

# Use Anthropic Claude 3.7 Sonnet Extended Thinking
# claude-haiku-4-5-20251001 

def call_llm(prompt, use_cache: bool = True):
    """
    Call Claude Haiku with optimized settings for cost and performance.
    
    Optimizations:
    - Reduced thinking budget (5000 tokens) - appropriate for Haiku's speed
    - Reduced max_tokens (8000) - covers most code/text tasks
    - Proper error handling and response parsing
    - Logging for debugging
    - Caching support
    
    Args:
        prompt: The input prompt
        use_cache: Whether to use cache (default: True)
    
    Returns:
        The LLM response text
    """
    from anthropic import Anthropic
    
    # Log the prompt
    logger.info(f"PROMPT: {prompt[:200]}..." if len(prompt) > 200 else f"PROMPT: {prompt}")
    
    # Check cache if enabled
    if use_cache:
        cache = {}
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache = json.load(f)
                if prompt in cache:
                    logger.info("RESPONSE: (from cache)")
                    return cache[prompt]
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
    
    try:
        # Initialize client with API key from environment
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            logger.error("ANTHROPIC_API_KEY not set")
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        client = Anthropic(api_key=api_key)
        
        # Get configurable settings from environment
        model = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
        max_tokens = int(os.getenv("ANTHROPIC_MAX_TOKENS", "8000"))
        thinking_budget = int(os.getenv("ANTHROPIC_THINKING_BUDGET", "5000"))
        
        # Make the API call with optimized settings
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            thinking={
                "type": "enabled",
                "budget_tokens": thinking_budget
            },
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Safely extract text from response
        response_text = None
        for content_block in response.content:
            if content_block.type == "text":
                response_text = content_block.text
                break
        
        if response_text is None:
            error_msg = f"No text content in response. Content types: {[c.type for c in response.content]}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Log the response
        logger.info(f"RESPONSE: {response_text[:200]}..." if len(response_text) > 200 else f"RESPONSE: {response_text}")
        
        # Update cache if enabled
        if use_cache:
            try:
                cache = {}
                if os.path.exists(cache_file):
                    try:
                        with open(cache_file, "r", encoding="utf-8") as f:
                            cache = json.load(f)
                    except:
                        pass
                
                cache[prompt] = response_text
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(cache, f, ensure_ascii=False)
            except Exception as e:
                logger.warning(f"Failed to save cache: {e}")
        
        return response_text
        
    except Exception as e:
        error_msg = f"LLM API call failed: {str(e)}"
        logger.error(error_msg)
        raise

# # Use OpenAI o1
# def call_llm(prompt, use_cache: bool = True):
#     from openai import OpenAI
#     client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "your-api-key"))
#     r = client.chat.completions.create(
#         model="o1",
#         messages=[{"role": "user", "content": prompt}],
#         response_format={
#             "type": "text"
#         },
#         reasoning_effort="medium",
#         store=False
#     )
#     return r.choices[0].message.content

# Use OpenRouter API
# def call_llm(prompt: str, use_cache: bool = True) -> str:
#     import requests
#     # Log the prompt
#     logger.info(f"PROMPT: {prompt}")

#     # Check cache if enabled
#     if use_cache:
#         # Load cache from disk
#         cache = {}
#         if os.path.exists(cache_file):
#             try:
#                 with open(cache_file, "r", encoding="utf-8") as f:
#                     cache = json.load(f)
#             except:
#                 logger.warning(f"Failed to load cache, starting with empty cache")

#         # Return from cache if exists
#         if prompt in cache:
#             logger.info(f"RESPONSE: {cache[prompt]}")
#             return cache[prompt]

#     # OpenRouter API configuration
#     api_key = os.getenv("OPENROUTER_API_KEY", "")
#     model = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-exp:free")
    
#     headers = {
#         "Authorization": f"Bearer {api_key}",
#     }

#     data = {
#         "model": model,
#         "messages": [{"role": "user", "content": prompt}]
#     }

#     response = requests.post(
#         "https://openrouter.ai/api/v1/chat/completions",
#         headers=headers,
#         json=data
#     )

#     if response.status_code != 200:
#         error_msg = f"OpenRouter API call failed with status {response.status_code}: {response.text}"
#         logger.error(error_msg)
#         raise Exception(error_msg)
#     try:
#         response_text = response.json()["choices"][0]["message"]["content"]
#     except Exception as e:
#         error_msg = f"Failed to parse OpenRouter response: {e}; Response: {response.text}"
#         logger.error(error_msg)        
#         raise Exception(error_msg)
    

#     # Log the response
#     logger.info(f"RESPONSE: {response_text}")

#     # Update cache if enabled
#     if use_cache:
#         # Load cache again to avoid overwrites
#         cache = {}
#         if os.path.exists(cache_file):
#             try:
#                 with open(cache_file, "r", encoding="utf-8") as f:
#                     cache = json.load(f)
#             except:
#                 pass

#         # Add to cache and save
#         cache[prompt] = response_text
#         try:
#             with open(cache_file, "w", encoding="utf-8") as f:
#                 json.dump(cache, f)
#         except Exception as e:
#             logger.error(f"Failed to save cache: {e}")

#     return response_text

if __name__ == "__main__":
    test_prompt = "Hello, how are you?"

    # First call - should hit the API
    print("Making call...")
    response1 = call_llm(test_prompt, use_cache=False)
    print(f"Response: {response1}")
