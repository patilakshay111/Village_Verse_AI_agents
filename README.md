# VillageVerse

Multi-agent Indian village simulation (Anandgaon).

## One-click start (Windows)

Double-click **`Run-VillageVerse.bat`** in this folder.

- Starts **one** server on port **8000** (API + built UI together)
- Opens **http://127.0.0.1:8000** in your browser
- No separate frontend window or Node.js needed after the UI is built once

Requires **Ollama** running for simulation ticks (`ollama serve`).

Optional dev mode (hot reload): run `Run-VillageVerse.bat`, then `Run-VillageVerse-Dev.bat` and open http://127.0.0.1:5173

## One-click stop

Double-click **`Stop-VillageVerse.bat`**, or close the two terminal windows titled **VillageVerse API** and **VillageVerse UI**.

## Manual start

See [backend/README.md](backend/README.md) and [frontend/README.md](frontend/README.md).
