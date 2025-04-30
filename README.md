# Smart Home Voice Control System

A Python-based smart home simulation system that allows voice control of home appliances through either online API or local LLM.
Github: https://github.com/1478387600/SmartHome/tree/simulation

## Features
- Simulates various home appliances (lights, AC, TV, etc.)
- Voice control
- Supports both online API and local LLM modes

## Prerequisites
- Python 3.10+
- Windows

## Installation & Setup

1. cd to this repository:
```bash
cd path/to/this/project
```

2. Create and activate a virtual environment (recommended):

Using Python's built-in venv:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

Or using uv (faster alternative):
```bash
uv venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install dependencies:

Using pip:
```bash
pip install -r requirements.txt
```

Or using uv (faster alternative):
```bash
uv pip install -r requirements.txt
```

## Running the Application

1. Run the main.py file in the root path of the project
2. Check the "Home Appliance Simulation" check box
3. Click "Run"
4. In the next window:
   - Click "Online API" to use cloud-based voice recognition
   - OR click "Local LLM" to use local language model
5. Focus on the terminal in your IDE (the software where the code is running) to interact with the system

## Project Structure
```
SmartHome/
├── client/               # Client-side implementation
│   ├── core/             # Core client functionality
│   ├── llm/              # Language model integrations
│   ├── runners/          # Application runners
│   ├── speech/           # Speech recognition and synthesis
│   └── strategies/       # Different LLM strategy implementations
│
├── environment/          # Home simulation environment
│   ├── images/           # Appliance images for GUI
│   └── *.py              # Simulation and visualization scripts
│
├── model/                # Device and sensor models
│   ├── base/             # Base classes
│   ├── devices/          # Specific appliance implementations
│   ├── Manager/          # Management classes
│   └── sensors/          # Sensor implementations
│
├── server/               # Backend server implementation
│   └── resources/        # Configuration files
│
├── main.py               # Main application entry point
├── requirements.txt      # Python dependencies
└── README.md            # Project documentation
```

## Troubleshooting
- If you encounter missing dependencies, run `pip install -r requirements.txt` again
- If you encounter a collision related to the version of dependancies, remove the version and leave just the name of library in the requirements.txt 
- For voice recognition issues, check your microphone settings
- Ensure you have stable internet connection when using Online API mode
- If you found that the MCP client could not be launch, try to run server/app.py in another terminal session manually first.
- I also encounter the problem that the tts is speaking but the computer doesn't make a sound from time to time, that's because bad luck.
- If you want to try the local LLM, please download the file on the huggingface (by searching "vlmbgnr/qwen2.5-1.5b-instruct-smarthome-lora-gguf-q4_o"), link = https://huggingface.co/vlmbgnr/qwen2.5-1.5b-instruct-smarthome-lora-gguf-q4_o/tree/main. Download it and put to project_folder\client\llm\models\qwen-q4_0.gguf and modify the MODEL_FILE in client\llm\config.py to make sure the path is correct.
- Strongly recommand to the API solution. There is an API key in the ".env" file, don't share it out.
## Contributors
All code files except those in the folder "environment": HengyuanWU_20717357
Simulator related files: NattapongNEADTIP_20717335
