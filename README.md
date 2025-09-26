# Wind Forecast Dashboard

This is an interactive web dashboard for visualizing and analyzing wind power generation forecasts. This dashboard displays the results of work completed during an NSF REU project at Washington State University Vancouver, comparing predictions from multiple forecasting models against historical power generation data from wind farms.

## Installation and Setup

1. Clone the repository on your local machine
    ```bash
    git clone https://github.com/jyao46/wind-forecast-dashboard.git
    cd wind-forecast-dashboard
    ```

2. Create a virtual environment to manage packages
    ```bash
    # Create virtual environment
    python -m venv .venv

    # Activate virtual environment
    # On macOS/Linux:
    source .venv/bin/activate

    # On Windows:
    .venv\Scripts\activate
    ```

3. Install dependencies
    ```bash
    pip install -r requirements.txt
    ```

4. Run the Application
    ```bash
    python app.py
    ```
    Open your web browser and navigate to: http://127.0.0.1:8050/

    The dashboard should load and be ready to use.