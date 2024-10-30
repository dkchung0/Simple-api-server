from fastapi import FastAPI, HTTPException, File, UploadFile
from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import pandas as pd
import os
import logging
from model import UserCreate

# Load environment variables from a .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    filename='test.log',  
    level=logging.INFO,   
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title="Test API",  # API title
    description="Pegatron Exam",  # API description
    version="1.0.0",  # API version
)

# Database configuration
DATABASE_URL = os.getenv('POSTGRESQL')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    """SQLAlchemy model for the 'users' table."""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    age = Column(Integer)

# Create tables in the database
Base.metadata.create_all(bind=engine)

@app.post("/users/")
def create_user(data: UserCreate):
    """
    Create a new user.
    
    Args:
    - data: UserCreate - User data to be added.
    
    Raises:
    - HTTPException: 400 if the user already exists, 
      422 if the user name is empty, 
      400 if the age is greater than 120.
    
    Returns:
    - A message indicating the creation status of the user.
    """
    db = SessionLocal()
    try:
        # Check if the user name is empty
        if not data.name:
            raise HTTPException(status_code=422, detail="User name cannot be empty")
        
        # Check if the age is greater than 120
        if data.age > 120:
            raise HTTPException(status_code=400, detail="User age cannot exceed 120 years")

        # Check if the user already exists
        query = text("SELECT * FROM users WHERE name = :name")
        result = db.execute(query, {"name": data.name}).fetchone()
        
        if result:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Create new user
        new_user = User(name=data.name, age=data.age)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logging.info(f"User '{data.name}' created successfully")
        return {"detail": f"User '{data.name}' created successfully"}
    
    except HTTPException as http_exc:
        # Specific exception handling for HTTPException
        logging.error(f"HTTPException: {str(http_exc.detail)}")
        raise http_exc  # Re-raise the HTTPException to preserve the status code
    
    except Exception as e:
        logging.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
    finally:
        db.close()

@app.delete("/users/{name}")
def delete_user(name: str):
    """
    Delete a user by name.
    
    Args:
    - name: str - The name of the user to be deleted.
    
    Raises:
    - HTTPException: 404 if the user is not found.
    
    Returns:
    - A detail message confirming the deletion.
    """
    db = SessionLocal()
    try:
        query = text("SELECT * FROM users WHERE name = :name")
        result = db.execute(query, {"name": name}).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        
        delete_query = text("DELETE FROM users WHERE name = :name")
        db.execute(delete_query, {"name": name})
        db.commit()

        logging.info(f"User '{name}' deleted successfully")
        return {"detail": f"User '{name}' deleted"}
    
    except HTTPException as http_exc:
        # Specific exception handling for HTTPException
        logging.error(f"HTTPException: {str(http_exc.detail)}")
        raise http_exc  # Re-raise the HTTPException to preserve the status code
    
    except Exception as e:
        logging.error(f"Error deleting user '{name}': {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
    finally:
        db.close()

@app.get("/users/")
def get_users():
    """
    Get a list of all users.
    
    Returns:
    - A list of all users.
    """
    db = SessionLocal()
    try:
        query = text("SELECT * FROM users")
        result = db.execute(query).fetchall()
        
        users = [dict(row) for row in result]

        logging.info("Retrieved all users successfully")
        return users
    
    except Exception as e:
        logging.error(f"Error retrieving users: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
    finally:
        db.close()

@app.post("/users/upload/")
def upload_users(file: UploadFile = File(...)):
    """
    Bulk upload users from a CSV file.
    
    Args:
    - file: UploadFile - The CSV file containing user data.
    
    Returns:
    - A detail message about the upload status.
    """
    db = SessionLocal()
    try:
        csv_data = pd.read_csv(file.file)

        for index, row in csv_data.iterrows():
            name = row['Name']
            age = row['Age']

            query = f"SELECT 1 FROM users WHERE name = '{name}'"
            result = db.execute(query).fetchone()

            if not result:
                insert_query = f"INSERT INTO users (name, age) VALUES ('{name}', {age})"
                db.execute(insert_query)
        
        db.commit()

        logging.info("Users from CSV uploaded successfully")
        return {"detail": "Users from CSV uploaded successfully"}
    
    except Exception as e:
        logging.error(f"Error uploading users from CSV: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
    finally:
        db.close()

@app.get("/users/average_age/")
def get_average_age_by_group():
    """
    Get the average age of users grouped by the first letter of their name.
    
    Returns:
    - A dictionary where keys are the first letter of names and values are average ages.
    
    Raises:
    - HTTPException: 404 if no users are found.
    """
    db = SessionLocal()
    try:
        query = text("SELECT name, age FROM users")
        result = db.execute(query).fetchall()
        
        if not result:
            raise HTTPException(status_code=404, detail="No users found")
        
        user_data = [{"name": row['name'], "age": row['age']} for row in result]
        df = pd.DataFrame(user_data)
        
        df['group'] = df['name'].str[0].str.upper()  # Extract first letter and convert to uppercase
        avg_age_by_group = df.groupby('group')['age'].mean().to_dict()

        logging.info("Average age by group retrieved successfully")
        return avg_age_by_group
    
    except HTTPException as http_exc:
        # Specific exception handling for HTTPException
        logging.error(f"HTTPException: {str(http_exc.detail)}")
        raise http_exc  # Re-raise the HTTPException to preserve the status code
    
    except Exception as e:
        logging.error(f"Error calculating average age by group: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
    finally:
        db.close()
