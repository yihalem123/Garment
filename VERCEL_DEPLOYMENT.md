# Vercel Deployment Guide

This guide will help you deploy your React frontend to Vercel.

## Prerequisites

1. A GitHub account (or GitLab/Bitbucket)
2. A Vercel account (sign up at https://vercel.com - free tier available)
3. Your code pushed to a Git repository
4. Your backend deployed on Render (you should have the backend URL)

## Step-by-Step Deployment Instructions

### Option 1: Deploy via Vercel Dashboard (Recommended)

1. **Push your code to GitHub**
   - Make sure all changes are committed and pushed to your repository

2. **Go to Vercel Dashboard**
   - Visit https://vercel.com/dashboard
   - Click "Add New..." → "Project"

3. **Import your repository**
   - Connect your GitHub account if not already connected
   - Select your repository
   - Click "Import"

4. **Configure the project**
   - **Framework Preset**: Vercel should auto-detect "Create React App"
   - **Root Directory**: Set to `frontend` (since your frontend is in a subdirectory)
   - **Build Command**: `npm run build` (should be auto-filled)
   - **Output Directory**: `build` (should be auto-filled)
   - **Install Command**: `npm install` (should be auto-filled)

5. **Set Environment Variables**
   - Click "Environment Variables"
   - Add the following variable:
     ```
     REACT_APP_API_URL=https://your-backend-service.onrender.com
     ```
   - Replace `your-backend-service.onrender.com` with your actual Render backend URL
   - Make sure to select all environments (Production, Preview, Development)

6. **Deploy**
   - Click "Deploy"
   - Wait for the build to complete (usually 2-5 minutes)
   - Your app will be live at `https://your-project.vercel.app`

### Option 2: Deploy via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

4. **Deploy**
   ```bash
   vercel
   ```
   - Follow the prompts
   - When asked for environment variables, add:
     ```
     REACT_APP_API_URL=https://your-backend-service.onrender.com
     ```

5. **For production deployment**
   ```bash
   vercel --prod
   ```

## Important Configuration

### Environment Variables

You **MUST** set the `REACT_APP_API_URL` environment variable in Vercel:

1. Go to your project in Vercel Dashboard
2. Click "Settings" → "Environment Variables"
3. Add:
   - **Name**: `REACT_APP_API_URL`
   - **Value**: `https://your-backend-service.onrender.com` (your Render backend URL)
   - **Environment**: Select all (Production, Preview, Development)

### Root Directory Configuration

Since your frontend is in the `frontend` subdirectory:

1. Go to Project Settings → General
2. Under "Root Directory", click "Edit"
3. Set it to `frontend`
4. Save

### CORS Configuration

Make sure your Render backend has the correct CORS settings:

1. Go to your Render service dashboard
2. Go to "Environment" settings
3. Update `ALLOWED_HOSTS_STR` to include your Vercel domain:
   ```
   https://your-project.vercel.app,https://your-project-git-main.vercel.app
   ```
   Or use `*` for development (not recommended for production)

## Post-Deployment

1. **Test the deployment**
   - Visit your Vercel URL: `https://your-project.vercel.app`
   - Try logging in
   - Verify API calls are working

2. **Check browser console**
   - Open browser DevTools (F12)
   - Check Console and Network tabs for any errors
   - Verify API calls are going to your Render backend

3. **Update backend CORS (if needed)**
   - If you see CORS errors, update `ALLOWED_HOSTS_STR` in Render
   - Add your Vercel domain(s) to the allowed hosts

## Custom Domain (Optional)

1. Go to Project Settings → Domains
2. Add your custom domain
3. Follow Vercel's DNS configuration instructions
4. Update `ALLOWED_HOSTS_STR` in Render to include your custom domain

## Troubleshooting

### Common Issues

1. **API calls failing**
   - Check that `REACT_APP_API_URL` is set correctly in Vercel
   - Verify your Render backend is running
   - Check browser console for CORS errors

2. **Build fails**
   - Check build logs in Vercel dashboard
   - Ensure all dependencies are in `package.json`
   - Try building locally: `cd frontend && npm run build`

3. **404 errors on page refresh**
   - The `vercel.json` file handles this with rewrites
   - If issues persist, check Vercel routing configuration

4. **Environment variables not working**
   - Remember: React environment variables must start with `REACT_APP_`
   - Rebuild after adding environment variables
   - Check that variables are set for the correct environment

### Getting Your Render Backend URL

1. Go to your Render dashboard
2. Click on your backend service
3. Your service URL will be shown at the top (e.g., `https://garment-backend.onrender.com`)
4. Use this URL (without trailing slash) for `REACT_APP_API_URL`

## Free Tier Limitations

- **Vercel**: 
  - 100GB bandwidth/month
  - Unlimited deployments
  - Automatic HTTPS
  - Custom domains supported

- **Render**:
  - Services spin down after 15 minutes of inactivity
  - First request after spin-down may take 30-60 seconds
  - Consider upgrading for always-on service

## Security Checklist

- [ ] Set `REACT_APP_API_URL` to your production backend URL
- [ ] Update backend CORS to only allow your Vercel domain (not `*`)
- [ ] Use HTTPS for all API calls (backend should be on HTTPS)
- [ ] Review and secure API endpoints
- [ ] Don't commit sensitive environment variables

## Support

- Vercel Docs: https://vercel.com/docs
- Vercel Community: https://github.com/vercel/vercel/discussions

