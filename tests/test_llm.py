from app.llm import GeminiClient

def test_missing_api_key():
    try:
        GeminiClient(api_key="")
    except RuntimeError as exc:
        assert "GEMINI_API_KEY" in str(exc)
    else:
        raise AssertionError(
            "GeminiClient should fail when GEMINI_API_KEY is missing."
        )


if __name__ == "__main__":
    test_missing_api_key()
    print("LLM configuration test passed.")