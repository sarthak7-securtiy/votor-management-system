# Voter Management System

A comprehensive voter management system built with Flask that allows for efficient management of voter data with Excel import/export capabilities.

## Features

- Excel-based voter data import with comprehensive field mapping
- Advanced booth name filtering to prevent incorrect data mapping
- User authentication and role-based access control
- Search and filter functionality for voter records
- Clear data functionality for administrators
- Star rating system for voters

## Deployment on Render

This project is configured for deployment on Render, a cloud hosting platform.

### Steps to Deploy:

1. **Create a Render Account**:
   - Go to [https://render.com](https://render.com) and sign up for an account

2. **Create a New Web Service**:
   - Click "New +" and select "Web Service"
   - Connect your GitHub/GitLab repository containing this project
   - Or use the "Import from GitHub" option

3. **Configure the Web Service**:
   - **Environment**: Select "Python"
   - **Branch**: Select your main branch (usually `main` or `master`)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT wsgi:app`

4. **Environment Variables**:
   - `SECRET_KEY`: Generate a secure secret key (Render can auto-generate this)
   - `DATABASE_URL`: For PostgreSQL database (Render will provide this if using their database service)

5. **Deployment**:
   - Click "Create Web Service"
   - Render will automatically build and deploy your application
   - The application will be accessible at the provided Render URL

### Important Notes:

- The system will automatically create the main user with credentials:
  - Username: `santosh ghanwat`
  - Password: `ghanwat@187514`
- The first deployment may take a few minutes as it installs all dependencies
- After deployment, you can access your voter management system at the Render-provided URL

### Custom Domain (Optional):

- You can connect a custom domain to your Render service in the Render dashboard
- Follow Render's instructions for DNS configuration

## Local Development

If you need to run locally:

```bash
pip install -r requirements.txt
python -m app.app
```

The application will run on `http://127.0.0.1:5000`

## Troubleshooting

- If deployment fails, check the build logs in Render dashboard
- Ensure all dependencies in `requirements.txt` are compatible
- Verify that the `wsgi.py` file correctly imports your Flask app
- Check that environment variables are properly set in Render