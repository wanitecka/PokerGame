# Flask Poker Game

This project is a web-based poker game built using Flask. It allows users to participate in a poker game while collecting data on their decisions and gameplay.

## Project Structure

```
flask-poker-game
├── app
│   ├── __init__.py          # Initializes the Flask application
│   ├── routes.py            # Contains route definitions and logic
│   ├── static
│   │   ├── css
│   │   │   └── styles.css    # CSS styles for the application
│   │   └── images
│   │   │   └── fond_poker.png # Background image for the application
│   │   └── cartes_images
│   │       └── [card_images_here].png # Images of playing cards used in the game
│   └── templates
│       ├── base.html        # Base template for the application
│       ├── index.html       # Homepage template
│       ├── form.html        # Template for participant information form
│       ├── preflop.html 
│       ├── flop.html 
│       ├── turn.html 
│       ├── river.html 
│       └── end.html         # End game results template
├── data
│   └── decisions.csv        # Stores participant decisions and game data
├── requirements.txt          # Lists project dependencies
├── runtime.txt               # Specifies Python version for the application
├── wsgi.py                   # Entry point for the WSGI server
└── README.md                 # Documentation for the project
```

## Setup Instructions

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd flask-poker-game
   ```

2. **Create a virtual environment**:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```
   python wsgi.py
   ```

5. **Access the game**:
   Open your web browser and go to `http://127.0.0.1:5000`.

## Usage

- Follow the on-screen instructions to enter your participant information and start playing the poker game.
- The game will collect data on your decisions and gameplay, which will be stored in `data/decisions.csv`.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License.