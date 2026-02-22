# Finance Depictor Project

## Overview
The Finance Depictor is a Python-based web application built with Flask, designed to visualise and categorise financial transactions extracted from PDFs. It allows users to view transaction data categorised by year, month, and category, and provides insights into different categories of spending.

## Features
- **PDF Processing**: Extracts transaction data from PDF statements using the `PDFContentConverter` and processes it into structured data.
- **Categorisation**: Organises transactions into predefined categories and subcategories. Users can add or remove categories and keywords.
- **Visualisation**: Displays transaction data through various views, including yearly summaries, monthly breakdowns, and specific category analyses.
- **Caching**: Utilises caching to improve performance and manage previously processed data.

## Components
- **Flask Application (`app.py`)**:
  - Main application script that sets up Flask routes and renders HTML templates.
  - Routes include year-based views, monthly breakdowns, category views, and more.

- **Category Management (`category_manager.py`)**:
  - Handles category management, including adding/removing categories and keywords, and saving/loading categories to/from JSON files.

- **Category Functions (`category_functions.py`)**:
  - Provides functionality for processing and aggregating transaction data based on categories and years.

- **PDF Processing (`PDF_stuff.py`)**:
  - Handles extraction and parsing of transaction data from PDF statements.
  - Converts PDF content into a DataFrame and manages caching of processed data.

## Usage
1. **Setup**: Ensure you have the necessary dependencies installed and the required PDF statements in place.
2. **Run the App**: Start the Flask application by running `python app.py`.
3. **Access**: Open your browser and navigate to `http://localhost:8070` to interact with the web application.

## Dependencies
- Flask
- pandas
- numpy
- PDFContentConverter

## TODOs
- unit tests
- add documentation
- add AI API call to add a suggestion on where to save.
- improve UI
- containerise
- look into OFX files instead of pdf files from each bank
