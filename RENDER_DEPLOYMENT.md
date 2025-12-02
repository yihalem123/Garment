# Render Deployment Guide

This guide will help you deploy your FastAPI backend to Render.

## Prerequisites

1. A GitHub account (or GitLab/Bitbucket)
2. A Render account (sign up at https://render.com)
3. Your code pushed to a Git repository

## Step-by-Step Deployment Instructions

### Option 1: Using render.yaml (Recommended)

1. **Push your code to GitHub**
   - Make sure all changes are committed and pushed to your repository

2. **Create a new Web Service on Render**
   - Go to https://dashboard.render.com
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` file
   - Click "Apply" to create the service and database

3. **Configure Environment Variables**
   - Go to your service settings
   - Add/update these environment variables:
     - `SECRET_KEY`: Generate a strong secret key (you can use: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
     - `ENVIRONMENT`: Set to `production`
     - `DEBUG`: Set to `false`
     - `ALLOWED_HOSTS`: Set to your frontend domain (e.g., `https://your-frontend.vercel.app,https://your-frontend.netlify.app`)
     - `DATABASE_URL`: This will be automatically set by Render when you create the database

### Option 2: Manual Setup (Without render.yaml)

1. **Create a PostgreSQL Database**
   - Go to Render Dashboard → "New +" → "PostgreSQL"
   - Choose a name (e.g., `garment-db`)
   - Select a plan (Free tier available)
   - Click "Create Database"
   - Copy the **Internal Database URL** (you'll need this)

2. **Create a Web Service**
   - Go to Render Dashboard → "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure the service:
     - **Name**: `garment-backend` (or your preferred name)
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
     - **Plan**: Choose Free, Starter, or Standard

3. **Set Environment Variables**
   - In your Web Service settings, go to "Environment"
   - Add these variables:
     ```
     DATABASE_URL=<your-postgres-internal-connection-string>
     SECRET_KEY=<generate-a-strong-secret-key>
     ENVIRONMENT=production
     DEBUG=false
     ALLOWED_HOSTS=*
     PYTHON_VERSION=3.11.0
     ```
   - **Important**: Use the **Internal Database URL** from your PostgreSQL service
   - The Internal URL looks like: `postgres://user:password@hostname:5432/dbname`

4. **Deploy**
   - Click "Save Changes"
   - Render will automatically build and deploy your service
   - Wait for the deployment to complete (usually 2-5 minutes)

## Important Notes

### Database Connection
- Render provides PostgreSQL connection strings in `postgres://` format
- The app automatically converts this to `postgresql+asyncpg://` format for async SQLAlchemy
- Make sure to use the **Internal Database URL** (not External) for better performance

### Port Configuration
- Render automatically sets the `$PORT` environment variable
- The start command uses `$PORT` to bind to the correct port
- Do NOT hardcode port 8000 in production

### CORS Configuration
- Update `ALLOWED_HOSTS` with your frontend domain(s)
- For development, `*` works, but for production, specify exact domains:
  ```
  ALLOWED_HOSTS=https://your-frontend.vercel.app,https://your-frontend.netlify.app
  ```

### Database Migrations
- After deployment, you may need to run database migrations
- You can do this via Render's Shell:
  1. Go to your service
  2. Click "Shell"
  3. Run: `alembic upgrade head`

### Health Check
- The app has a `/health` endpoint at: `https://your-service.onrender.com/health`
- Render will use this for health checks

## Post-Deployment

1. **Test the API**
   - Visit: `https://your-service.onrender.com/docs` for Swagger UI
   - Visit: `https://your-service.onrender.com/health` to check health

2. **Update Frontend**
   - Update your frontend's API URL to point to your Render service
   - Example: `REACT_APP_API_URL=https://your-service.onrender.com`

3. **Monitor Logs**
   - Check Render dashboard for deployment logs
   - Monitor for any errors or warnings

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Ensure you're using the Internal Database URL
   - Check that the database is running
   - Verify DATABASE_URL environment variable is set correctly

2. **Build Failures**
   - Check that all dependencies are in `requirements.txt`
   - Ensure Python version matches (3.11.0)

3. **Port Binding Errors**
   - Make sure start command uses `$PORT` not hardcoded port
   - Command should be: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **CORS Errors**
   - Update ALLOWED_HOSTS with your frontend domain
   - Check that CORS middleware is properly configured

## Free Tier Limitations

- Services spin down after 15 minutes of inactivity
- First request after spin-down may take 30-60 seconds
- Consider upgrading to Starter plan ($7/month) for always-on service

## Security Checklist

- [ ] Generate a strong SECRET_KEY
- [ ] Set DEBUG=false in production
- [ ] Update ALLOWED_HOSTS with specific domains
- [ ] Use Internal Database URL (not External)
- [ ] Enable HTTPS (automatic on Render)
- [ ] Review and secure API endpoints

## Support

- Render Docs: https://render.com/docs
- Render Community: https://community.render.com

