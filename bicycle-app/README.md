<p align="center">
  <a href="https://nextjs-fastapi-starter.vercel.app/">
    <img src="https://assets.vercel.com/image/upload/v1588805858/repositories/vercel/logo.png" height="96">
    <h3 align="center">Next.js FastAPI Starter</h3>
  </a>
</p>

<p align="center">Simple Next.js boilerplate that uses BOTH <a href="https://fastapi.tiangolo.com/">FastAPI</a> AND NEXTJS 13 as the API backend unlike <a href="https://github.com/digitros/nextjs-fastapi" >the example offered by NextJS</a>

<br/>

## Introduction

This is a hybrid Next.js + Python app that uses a fullstack Next.js application and FastAPI as another API backend. 

**NOTE:** You may have jittery video if running the application via `npm run dev` in your web browser. This is because _some_ browsers will open two websocket connections due to the way React manages it's state in development in the page load `useEffect`. If you instead do a `npm run build`, followed by an `npm run start`, you should see the completely optimized experience.

## How It Works

The Python/FastAPI server is mapped into to Next.js app under `/api/py/`(easily changeable) and the NextJS is mapped to `/api/`.

## Getting Started

First, install the dependencies:

```bash
npm install
# or
yarn
# or
pnpm install
```

Create a virtual environment and install the dependencies for the FastAPI server:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Then, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

The FastApi server will be running on [http://127.0.0.1:8000](http://127.0.0.1:8000) – feel free to change the port in `package.json` (you'll also need to update it in `next.config.js`).
