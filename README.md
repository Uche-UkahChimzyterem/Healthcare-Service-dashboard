
# Healthcare Service Quality Dashboard

Interactive dashboard for analyzing customer and staff reviews across healthcare facilities, built with Dash and Plotly.

## Features
- Review Analytics: Visualize distribution by service category
- Facility Comparison: Compare government vs private hospitals
- Interactive Components: Dropdown filters and data tables
- Responsive Design: Works on desktop and mobile

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Uche-UkahChimzyterem/Healthcare-Service-dashboard
   cd healthcare-service-dashboard
   ```

2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

3. Add your data file:
   - Place `Review_Category_Report.xlsx` in the `Data/` folder
   - Required columns: 
     - `Company Name`
     - `Standardized Category` 
     - `Review Count`
     - `Company Type`

## Usage
Run the dashboard:
```bash
python app.py
```
Access at: `http://127.0.0.1:8050/` 

## Data Processing
- Cleans and standardizes:
  - Company types (e.g., converts "Modern/High-Class Private Hospital" to "High-Class Private Hospital")
  - Service categories (8 standardized categories)
- Handles missing data and type conversions

## Configuration
Customize in `app.py`:
```python
# Color scheme
colors = {
    'government': '#2563eb',      # Blue
    'small_private': '#ef4444',   # Red
    'high_class': '#10b981'       # Green
}

# Layout settings
app.layout = dbc.Container(..., style={'maxWidth': '1400px'})
```

## Deployment Options
1. Local Network:
   ```bash
   python app.py --host=0.0.0.0 --port=8050
   ```

2. Cloud Deployment:
   - Heroku, Render, or PythonAnywhere

## Troubleshooting
| Issue | Solution |
|-------|----------|
| Missing data file | Ensure `Data/Review_Category_Report.xlsx` exists |
| Import errors | Run `pip install -r requirements.txt` |
| Stale data | Restart the app after data changes |

Developed by Uche-Ukah Chimzyterem | © 2025
