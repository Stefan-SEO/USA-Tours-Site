# USA Tours Directory

A web application that showcases tours across the United States, organized by state.

## Features

- Browse tours by state
- View detailed information about each tour
- Pagination for states with many tours
- Simple and clean user interface

## Setup and Installation

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python app.py
   ```
4. Open your browser and navigate to `http://localhost:5000`

## Data

The tour data is sourced from the `Final-Viator-Tours.csv` file, which contains information about various tours across the United States.

## Project Structure

- `app.py`: Main application file
- `templates/`: HTML templates
- `static/`: Static files (CSS, JavaScript)
- `data/`: Data processing scripts 

## Deployment to Vercel

This application is configured for deployment on Vercel. Follow these steps to deploy:

1. Create a Vercel account at [vercel.com](https://vercel.com) if you don't have one
2. Install the Vercel CLI:
   ```
   npm install -g vercel
   ```
3. Login to Vercel from the CLI:
   ```
   vercel login
   ```
4. From the project directory, run:
   ```
   vercel
   ```
5. Follow the prompts to complete the deployment

### Configuration Files

The following files are included for Vercel deployment:
- `vercel.json`: Configuration for Vercel deployment
- `requirements.txt`: Python dependencies
- `wsgi.py`: WSGI entry point for the application

### Environment Variables

If your application requires environment variables, you can set them in the Vercel dashboard or using the Vercel CLI:
```
vercel env add MY_VARIABLE
```

### Continuous Deployment

Vercel supports continuous deployment from GitHub. Connect your GitHub repository to Vercel for automatic deployments when you push changes. 