# Log to OCEL2 Converter

This project is a Python application with a graphical user interface (GUI) built using **Tkinter**. It allows users to map log data from a JSON file into an OCEL2 (Object-centric Event Log) format. This tool is developed for a Master's thesis in **Business Informatics and Data Science** at the **University of Camerino**.

## Features

- **File Mapping**: Import log data in JSON format and map it into the OCEL2 format.
- **Tkinter GUI**: Easy-to-use interface for file selection, preview, and export functionality.
- **Multiple Exports**: Export your data into two formats: JSON and JSONOCEL.

## Setup

To set up the project, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/log-to-ocel.git
   ```

2. **Navigate to the project directory**:
   ```bash
   cd log-to-ocel
   ```

3. **Install dependencies**:
   Run the following command to install all required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   To start the application, execute the following command:
   ```bash
   python app.py
   ```

## Usage

1. **Set your log file**: Use the file selection dialog to choose your input log file in JSON format.
2. **Map data**: The app allows you to configure how the data is mapped to OCEL2 format.
3. **Preview and export**: Preview your mapped data and then export it into two formats: JSON and JSONOCEL.

## Requirements

- Python 3.8 or higher
- Tkinter
- PM4Py (for OCEL2 file handling)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
