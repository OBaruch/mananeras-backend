# YouTube Video Analysis Service

This project is a FastAPI application that provides an API for downloading YouTube video audio, transcribing it, performing text analysis, and storing the results in a PostgreSQL database.

## Core Functionalities

*   **Video Processing**: Downloads audio from YouTube videos.
*   **Transcription**: Transcribes the downloaded audio into text using Whisper.
*   **Text Analysis**: Performs several NLP tasks on the transcribed text, including:
    *   Summarization
    *   Extraction of bullet points
    *   Discourse classification
    *   Identification of main topics
    *   Political categorization
    *   Sentiment analysis
*   **Database Storage**: Stores video information, transcriptions, and analysis results in a PostgreSQL database using SQLAlchemy.
*   **API Endpoints**: Exposes FastAPI endpoints to:
    *   Add new videos.
    *   Retrieve video information.
    *   Generate and retrieve summaries and analyses for specific videos.
    *   Automatically fetch, process, and summarize the latest video from a predefined YouTube channel.

## Technologies Used

*   **FastAPI**: For building the RESTful API.
*   **SQLAlchemy**: For ORM interaction with the PostgreSQL database.
*   **PostgreSQL**: As the relational database management system.
    *   *About PostgreSQL*: PostgreSQL is a powerful, open-source object-relational database system known for its reliability, data integrity, robust feature set, and extensibility. It uses and extends the SQL language and can handle complex data workloads.
*   **yt-dlp**: For downloading video content from YouTube.
*   **Whisper (OpenAI)**: For audio transcription.
*   **Hugging Face Transformers (google/flan-t5-base)**: For text analysis tasks.
*   **Railway (Deployment Platform)**:
    *   *About Railway*: Railway is a modern deployment platform that simplifies the process of deploying applications. It allows developers to focus on their code without worrying extensively about infrastructure management, Docker, or clusters. It often integrates well with services like PostgreSQL. This project is likely intended to be (or can be easily) deployed on Railway, given the `Procfile` and typical Railway workflows. The `DATABASE_URL` environment variable mentioned in `database.py` is a common convention for connecting to databases provisioned by platforms like Railway.

## Project Structure

```
.
├── .gitignore
├── Dockerfile
├── LICENSE
├── Procfile             # Defines commands for starting the application (used by platforms like Heroku/Railway)
├── README.md            # This file
├── crud.py              # Contains CRUD (Create, Read, Update, Delete) operations for the database
├── database.py          # Database engine setup and session management
├── main.py              # Main FastAPI application, defines API endpoints
├── models.py            # SQLAlchemy models representing database tables (Video, Resumen)
├── requirements.txt     # Python package dependencies
├── schemas.py           # Pydantic schemas for data validation and serialization
└── utils/
    ├── __init__.py
    └── transcriber.py   # Utility functions for downloading, transcribing, and analyzing video text
```

## Setup and Running the Project

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Set up Environment Variables:**
    *   The application requires a `DATABASE_URL` environment variable to connect to your PostgreSQL instance. For example:
        ```
        DATABASE_URL="postgresql://user:password@host:port/database_name"
        ```
    *   You might need to configure other environment variables if specific API keys or settings are required for `yt-dlp` or other services, though not explicitly shown in the current file structure.

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *Note: Ensure you have FFmpeg installed on your system as it's a dependency for `yt-dlp`'s audio extraction.*

4.  **Initialize the database:**
    The `Base.metadata.create_all(bind=engine)` line in `main.py` will create the database tables when the application starts if they don't already exist.

5.  **Run the application:**
    Use Uvicorn (a fast ASGI server) to run the FastAPI application:
    ```bash
    uvicorn main:app --reload
    ```
    The `--reload` flag enables auto-reloading during development.

## API Endpoints

*   `GET /`: Home endpoint.
*   `POST /api/videos`: Create a new video entry.
*   `GET /api/videos`: Get a list of all videos.
*   `POST /api/videos/{video_id}/resumen`: Create a summary for a specific video.
*   `GET /api/videos/{video_id}/resumen`: Get the summary for a specific video.
*   `POST /api/videos/{video_id}/auto-resumen`: Automatically generate and store a summary for a video.
*   `POST /api/auto-resumen/latest`: Automatically fetch the latest video from a predefined YouTube channel, process it, and store its summary.

## How Railway is Used (Presumed)

*   **Deployment**: The `Procfile` (`web: uvicorn main:app --host 0.0.0.0 --port $PORT`) suggests the application is intended for deployment on platforms like Railway, which use Procfiles to determine how to run web services.
*   **Database Provisioning**: Railway can easily provision PostgreSQL databases. The `DATABASE_URL` environment variable in `database.py` would be set by Railway to point to the provisioned database instance.
*   **Simplified Infrastructure**: Railway handles much of the underlying infrastructure, allowing developers to deploy by connecting their Git repository and letting Railway build and run the application based on files like `requirements.txt` and `Procfile`.
