# FastAPI Application

This is a FastAPI application that provides basic user management APIs, including creating, deleting, listing, and bulk uploading users. The application uses Docker to simplify deployment and running.

## Directory Structure

.
├── Dockerfile
├── requirements.txt
├── main.py
├── model.py
├── test_main.py
└── README.md

## Environment Variables

Before using the application, you need to create a `.env` file to set up the PostgreSQL connection details. Create a file named `.env` in the root directory of the project and include the following content:

```plaintext
POSTGRESQL=postgresql://<username>:<password>@<hostname>:<port>/<database>
```

## Features

- **User Management API**:
  - `POST /users/`: Create a new user.
  - `DELETE /users/{name}`: Delete a user by name.
  - `GET /users/`: Retrieve all users.
  - `POST /users/upload/`: Bulk upload user data from a CSV file.
  - `GET /users/average_age/`: Get the average age of users grouped by the first letter of their names.


## Using Docker

### Build Docker Image

Navigate to the directory containing the `Dockerfile` and `requirements.txt`, then build the Docker image using:

```bash
sudo docker build -t my_fastapi_app .
sudo docker run -d -p 8080:8080 my_fastapi_app
```

### Access the Application

Open your web browser and navigate to the following address to access your FastAPI application:

http://localhost:8080