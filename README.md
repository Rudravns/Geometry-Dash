# Geometry dash Remake

A lightweight Python remake of Geometry Dash — a fast-paced side-scrolling platformer where the player times jumps to pass obstacles to the beat. This repository contains the source for the remake, built with Python and designed to be easy to run, extend, and learn from.

---

## Features

- Core Geometry Dash gameplay loop (automatic forward movement, timed jumping)
- Multiple levels / stage support (configurable)
- Simple physics and collision handling
- Score / progress tracking
- Keyboard controls (configurable)
- Easy-to-read Python code intended for learning and modification
- level editor

---

## Demo

placeholderr demo GIF or short video here when available:

![Demo Placeholder](docs/demo.gif)

---

## Requirements

- Python 3.8 or newer
- Recommended: virtualenv or venv for an isolated environment
- Typical dependency: pygame (or other framework used in the project)

Install pygame (example):
```bash
pip install pygame
```

If a `requirements.txt` is included in the repository:
```bash
pip install -r requirements.txt
```

---

## Installation

1. Clone the repository
```bash
git clone https://github.com/Rudravns/Geometry-Dash.git
cd Geometry-Dash
```

2. Create a virtual environment (optional but recommended)
```bash
python -m venv venv
# On macOS / Linux
source venv/bin/activate
# On Windows (PowerShell)
.\venv\Scripts\Activate.ps1
```

3. Install dependencies
```bash
pip install -r requirements.txt
# or, at minimum:
pip install pygame
```

---

## Running the game

Run the main script. Depending on the project layout it may be named `main.py`, `game.py`, or be available as a package entrypoint. Example:
```bash
python main.py
```
If the repository uses a package structure:
```bash
python -m geometry_dash
```

If you see errors, check the repository root for a README or a `docs/` folder describing the exact entrypoint.

---

## Controls

Default keyboard controls (common setup — confirm by checking the code):
- Space / Up Arrow: Jump
- Down Arrow: Hold to fall faster (if implemented)
- Esc: Pause / quit

Controls can be changed in the game settings or the input handling module.

---

## Project structure (suggested)

- assets/ — images, audio, fonts
- levels/ — level definitions (JSON, TXT, or Python)
- src/ or geometry_dash/ — main Python package
- main.py — entrypoint

Adjust based on the actual repository layout.

---

## Contributing

Contributions are welcome! A few suggestions to get started:
- Open an Issue for feature requests or bugs
- Fork the repo and create a feature branch for changes
- Keep changes focused and provide tests or a short demonstration for new features

Suggested workflow:
1. Fork → create branch → make changes → open a Pull Request

Coding style: follow PEP 8 for Python. Include docstrings for new modules/functions.

---

## Roadmap / Ideas

- More polished graphics and particle effects
- Soundtrack syncing and level editor
- Checkpoints and level progress saving
- Mobile controls / controller support
- Additional game modes (practice, endless, custom levels)

---

## Known issues

Currently in devolopment phase, please report any bugs

---

## License

Free creative license



---

## Credits

- Created by Rudravns and Kian
- Assets, music, and additional libraries should credit original creators where applicable.

---

## Contact

For questions or collaboration, open an issue or reach out via GitHub: [Rudravns](https://github.com/Rudravns)
