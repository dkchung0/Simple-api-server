import unittest
from fastapi.testclient import TestClient
from main import app  # Import the FastAPI application instance from the main module

client = TestClient(app)  # Create an instance of TestClient for making requests to the FastAPI app

class TestCreateUserAPI(unittest.TestCase):
    """
    Unit tests for the FastAPI create_user endpoint.
    """

    def test_create_user_name_empty(self):
        """
        Test case for when the user name is empty in the create_user API request.
        
        This test checks if the API correctly responds with a 422 status code and
        an appropriate error message when the user name field is empty.
        """
        response = client.post("/users/", json={"name": "", "age": 66})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json(), {"detail": "User name cannot be empty"})
    
    def test_create_user_age_exceeds_limit(self):
        """
        Test case for when the user age exceeds the maximum allowed value in the create_user API request.
        
        This test checks if the API correctly responds with a 400 status code and
        an appropriate error message when the user age exceeds 120 years.
        """
        response = client.post("/users/", json={"name": "Wukong", "age": 999})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "User age cannot exceed 120 years"})

if __name__ == "__main__":
    unittest.main()