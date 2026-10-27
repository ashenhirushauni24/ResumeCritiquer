# ResumeCritiquer

ResumeCritiquer is a small AI-powered resume review app built with Streamlit. Upload a PDF or plain-text resume, optionally enter a target job role, and receive practical feedback generated with Google Gemini.

## Features

- Upload PDF and UTF-8 plain-text (`.txt`) resumes.
- Extract selectable text from PDF pages or read text files.
- Optionally tailor the review to a target role.
- Get constructive feedback on clarity, skills, experience descriptions, grammar, formatting, and practical improvements.
- Handle missing API configuration, unreadable files, and empty analysis results with in-app messages.

> Scanned PDFs without selectable text may not be readable. Use a text-based PDF or a `.txt` file instead.

## Tech stack

- Python 3.13+
- Streamlit
- Google Gen AI SDK (Gemini)
- PyPDF2 for PDF text extraction
- `python-dotenv` for local environment configuration
- `uv` for dependency and environment management

## Requirements

- Python 3.13 or newer
- [`uv`](https://docs.astral.sh/uv/)
- A Google AI Studio API key with access to the Gemini API

## Setup

1. Clone the repository and move into the project directory:

   ```bash
   git clone <your-repository-url>
   cd ResumeCritiquer
   ```

2. Create and activate a virtual environment, then install the project dependencies with `uv`:

   ```bash
   uv sync
   ```

   `uv sync` creates the project environment and installs the dependencies recorded for this project.

3. Create a `.env` file in the project root and add your API key:

   ```dotenv
   GOOGLE_API_KEY=your_google_api_key_here
   ```

   Keep this key private. Do not commit `.env` or paste your real key into the README. If you prefer, set `GOOGLE_API_KEY` in your shell environment instead.

4. Start the app:

   ```bash
   uv run streamlit run src/resumecritiquer/main.py
   ```

5. Open the local URL printed in the terminal (Streamlit usually uses `http://localhost:8501`). Choose a PDF or TXT resume, optionally enter a target role, and select **Analyze my resume**.

## Project structure

```text
src/resumecritiquer/
├── main.py             # Streamlit interface and file handling
├── ai_analyzer.py      # Gemini prompt and analysis request
├── resume_parser.py    # Resume parsing module
├── report_generator.py # Report generation module
├── utils.py            # Package entry-point placeholder
└── sample_cv.txt       # Sample resume text
```

The current Streamlit interface performs PDF and TXT extraction in `main.py`. The parser and report-generator modules are present in the repository but are not currently used by that interface.

## Configuration and privacy

The app reads `GOOGLE_API_KEY` from the environment or a root-level `.env` file. Resume text is sent to the Gemini API to generate the requested feedback. Avoid uploading sensitive information unless you are comfortable sending it to that service, and review Google's API data handling terms for your account and configuration.

## Screenshots

No screenshot is included in the repository yet. Add one when available, for example at `docs/screenshots/home.png`, and update this section:

```markdown
![ResumeCritiquer app screenshot](docs/screenshots/home.png)
```

## Contributing

Contributions are welcome. Open an issue to discuss a substantial change, then submit a pull request with a clear description of the update.

## License

No license file is currently included. Add a `LICENSE` file before describing this project as open source or reusing it under specific license terms.
