# Storyboard Generator

A simple desktop application for creating, editing, and exporting storyboards for film production.

## Features

- Create and manage storyboard projects
- Add panels with images and text details
- Arrange panels in any order
- Save your project to work on later
- Export the storyboard as a PDF file

## Installation

### Option 1: Easy Installation (Recommended)

1. Make sure you have Python installed on your computer. If not, download and install it from [python.org](https://python.org).

2. Download this project and unzip it to a folder on your computer.

3. Run the launcher script:
   - **Windows**: Double-click on `launch.bat`
   - **Mac/Linux**: Open a terminal, navigate to the folder, and run `python launch.py`

   The launcher will automatically install any required dependencies.

### Option 2: Manual Installation

1. Make sure you have Python installed on your computer.

2. Open a terminal/command prompt and navigate to the project folder.

3. Install the required dependencies:

4. Run the application: python main.py


## Usage

### Creating a New Storyboard

1. Start the application
2. Click "File" > "New Project"
3. Add panels using the "Add" button on the left side
4. For each panel:
- Upload an image (JPG or PNG)
- Fill in the shot details (number, scene, camera, etc.)
- Add action descriptions and technical information
5. Use the "Up" and "Down" buttons to arrange your panels
6. Click "File" > "Save Project" to save your work

### Exporting as PDF

1. Once your storyboard is ready, click "File" > "Export to PDF"
2. Choose a location to save the PDF file
3. The PDF will show all your panels in a professional layout

## Troubleshooting

If you encounter any issues:

1. Make sure you have Python 3.7 or newer installed
2. Try reinstalling the dependencies manually: pip install --upgrade -r requirements.txt

3. Check that you have write permissions in the folder where you're saving projects

## License

[MIT License](LICENSE)
