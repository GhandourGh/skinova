# Deployment Guide for Render

## Quick Setup on Render (Free Tier)

### Step 1: Create Render Account
1. Go to https://render.com
2. Sign up for a free account (use GitHub to sign in)

### Step 2: Create PostgreSQL Database
1. In Render dashboard, click "New +" → "PostgreSQL"
2. Name: `skinova-db`
3. Database: `skinova`
4. User: `skinova_user`
5. Region: Choose closest to your location
6. Plan: **Free** (90 days free, then $7/month)
7. Click "Create Database"
8. **Copy the "Internal Database URL"** - you'll need this!

### Step 3: Deploy Web Service
1. In Render dashboard, click "New +" → "Web Service"
2. Connect your GitHub repository: `GhandourGh/skinova`
3. Configure:
   - **Name**: `skinova-clinic`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Root Directory**: (leave empty)
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn skinova_project.wsgi:application`

### Step 4: Add Environment Variables
In your Web Service settings, add these environment variables:

- `SECRET_KEY`: (Generate a random key - Render can auto-generate this)
- `DEBUG`: `False`
- `ALLOWED_HOSTS`: `your-app-name.onrender.com` (replace with your actual Render URL)
- `DATABASE_URL`: (Paste the Internal Database URL from Step 2)

### Step 5: Deploy!
1. Click "Create Web Service"
2. Wait for deployment (5-10 minutes first time)
3. Your app will be live at `https://your-app-name.onrender.com`

### Step 6: Run Initial Setup
After first deployment, you need to create a superuser:
1. Go to your service's "Shell" tab in Render
2. Run: `python manage.py createsuperuser`
3. Follow prompts to create admin user

## Access Your App
- **Admin Panel**: `https://your-app-name.onrender.com/admin/`
- **Main Site**: `https://your-app-name.onrender.com/`

## Making Updates
1. Make changes in Cursor
2. Commit: `git add . && git commit -m "your message"`
3. Push: `git push`
4. Render auto-deploys on push!

## Free Tier Limitations
- Web service sleeps after 15 min of inactivity
- First request after sleep takes ~30 seconds to wake up
- Database is free for 90 days, then $7/month
- Unlimited deployments!

## Troubleshooting
- Check logs in Render dashboard if deployment fails
- Make sure all environment variables are set correctly
- Database migrations run automatically via build.sh

