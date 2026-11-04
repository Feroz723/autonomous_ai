    if provider == "auto" and not candidates:
        reason = "no provider API key configured"
    else:
        reason = "; ".join(errors) or f"could not initialize provider {provider}"

    fallback_enabled = os.getenv("LLM_FALLBACK_TO_DUMMY", "true").strip().lower() in {
        "1", "true", "yes", "on"
    }
    if fallback_enabled:
        print(f"⚠️ LLM degraded mode: using dummy client ({reason})")
        return DummyClient()
    return _raise_missing_provider(reason)


def _raise_missing_provider(reason: str):
    raise RuntimeError(
        f"No usable LLM provider: {reason}. Set USE_DUMMY_LLM=true for intentional offline mode, "
        "or configure LLM_PROVIDER and its API key."
    )
