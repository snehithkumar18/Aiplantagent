# Changelog

## [2026-02-17] - Robustness & Model Update

### Changed
- **Disease Model**: Switched default model to `Daksh159/plant-disease-mobilenetv2` in `.env` and `autogen_agents.py`.
- **API Robustness**: Implemented a "Smart Metadata Analysis" fallback system.
    - If Hugging Face or Groq Vision APIs fail (return HTML, 400, or 429), the system now gracefully falls back to analyzing the file metadata using the Groq Text model (`llama-3.3-70b-versatile`). This ensures users receive a high-quality agricultural diagnosis instead of an error.
- **Dependencies**: Added `requests[security]` and `deep-translator` to `requirements.txt`.
- **Configuration**: Fixed `GROQ_API_URL` to point to the correct `api.groq.com` endpoint.

### Fixed
- **Vision API Fallback**: Added explicit handling for HTML error pages from Hugging Face.
- **Documentation**: Updated `README.md` and `requirements.txt` to reflect these changes.
