# TiDB_Data_Assistant

Welcome to the **TiDB_Data_Assistant**, the robust API backend for the **EmbraceAI_FrontEnd** application. This project is designed to handle complex data processing tasks involving emotion recognition and mindfulness exercise recommendation. It integrates with advanced AI models, including convolutional neural networks (CNNs), encoding models, and reinforcement learning (RL) models.

## Overview

The **TiDB_Data_Assistant** is a pivotal component of our submission for the **TiDB Hackathon 2024**. This backend API manages the communication and data flow between the front-end application and our AI models, ensuring efficient processing of emotional data to recommend personalized mindfulness exercises.

## Installation

### Prerequisites

- Ensure Python is installed on your system.
- The application should be run within a virtual environment to manage dependencies efficiently.

### Virtual Environment Setup

To set up a Python virtual environment, execute the following commands in your terminal:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
python app.py
```

### Features
Real-Time Data Processing: Handles large volumes of emotional data through CNNs.
Mindfulness Recommendations: Employs an RL model to deliver tailored mindfulness exercises based on user emotions.
Interactive API: Provides endpoints for the front-end to send and retrieve data seamlessly.

### Contributions
Contributions are welcome. Please feel free to fork the repository, make changes, and submit a pull request. Your input helps make our project even better!

### License
MIT License#
