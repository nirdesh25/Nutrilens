# How to Start NutriLens AI

## Step 1: Start Backend Server

Open a terminal and run:

```bash
cd nutrilens-ai/backend
python main.py
```

The backend will start on **http://localhost:8000**

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Step 2: Start Frontend Server

Open a NEW terminal (keep backend running) and run:

```bash
cd nutrilens-ai/frontend
npm run dev
```

The frontend will start on **http://localhost:3000**

You should see:
```
- ready started server on 0.0.0.0:3000, url: http://localhost:3000
- event compiled client and server successfully
```

## Step 3: Access the Application

Open your browser and go to: **http://localhost:3000**

## Troubleshooting

### Backend won't start
- Make sure Python is installed: `python --version`
- Install dependencies: `pip install -r requirements.txt`
- Check if port 8000 is already in use

### Frontend won't start
- Make sure Node.js is installed: `node --version`
- Install dependencies: `npm install`
- Clear cache: `rm -rf .next` then `npm run dev`
- Check if port 3000 is already in use

### Pages are blank
- Check browser console (F12) for errors
- Verify backend is running on port 8000
- Try accessing http://localhost:8000/docs to verify backend is working
