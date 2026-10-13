# Pl@ntNET plant recognition

A small FastAPI demo that sends a plant photo to Pl@ntNet and returns the most likely matches. I made it to try using an API key with an AI-powered service.

## Run it

You’ll need Python and your own Pl@ntNet API key.

1. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and add your key:

   ```env
   PLANTNET_API_KEY=your_key_here
   ```

3. Start the app:

   ```bash
   uvicorn demo:app --reload
   ```

4. Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs), choose `POST /identify`, upload a photo, and try it.

The `organ` field is optional. It accepts `auto`, `leaf`, `flower`, `fruit`, or `bark`.

Each request uses your Pl@ntNet API quota. Keep your API key in `.env` and don’t commit it.
