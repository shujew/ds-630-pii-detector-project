# PII Detector Final Project

Projects which traverses a given path, analyzes discovered files for PII, and generate a report output.

## Directory Structure

- `src/`: source code for app
- `src/parsers/`: parsers to extract text from multiple file formats
- `src/parsers/detectors`: pii detectors using Presidio, PIIAnalyzer, PIICatcher
- `sample_data/` : sample documents to be analyzed
- `sample_data_lite/` : sample documents to be analyzed with less files
- `images/`: images used in README
## Installation
### (For Windows Users) Microsoft Visual C++ Redistributable

Please install https://docs.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170

### (For MacOS Users) Brew Packages

1. Install [Home Brew](https://brew.sh/) if you don't have it
2. Install dependencies using commands below
```
brew install --cask xquartz
brew install poppler antiword unrtf tesseract swig
```
### Java 8

1. Install Java 8 from [official website](https://www.oracle.com/java/technologies/downloads/#java8). You will need to create a free account if you don't have an Oracle account.
2. **On Windows ONLY**, set the `JAVA_HOME` environment variable as described in [this article](https://confluence.atlassian.com/doc/setting-the-java_home-variable-in-windows-8895.html). If you don't have time to read, just follow bullet points below.

- Find your java installation folder. It is usually in the form `C:\Program Files\Java\jdk1.8.0_XX` where XX is the version number. For example, mine is `C:\Program Files\Java\jdk1.8.0_311`
- Run `setx -m JAVA_HOME "C:\Program Files\Java\jdk1.8.0_XX"`. Make sure to replace with actual folder name. For example, I have to run `setx -m JAVA_HOME "C:\Program Files\Java\jdk1.8.0_311"`

### Python dependencies

Switch to your virtual environment and run `pip install -r requirements.txt`

## Usage

Note:

- On Windows, reading `.doc` fails because antiword package is not available
- **PLEASE** be sure to follow instructions in `SETUP` before running this project

### Command Line Interface

```
python src/cli.py  -h
usage: cli.py [-h] path results

Scan a folder for PII

positional arguments:
  path        folder path to scan
  results     where to place results

optional arguments:
  -h, --help  show this help message and exit
```

![](images/running.png)

See `results.csv` for output example

### Graphical Interface 

`streamlit run src/app.py`

![](images/gui_screenshot.jpg)
