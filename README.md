Sensitive Data Scanner
This project is a Flask-based web application that scans uploaded .txt files for sensitive data like PAN, SSN, credit card numbers, health IDs, and more. The application uses a SQLite database to store and classify the sensitive information.

Features
Upload .txt files for scanning sensitive data.
Classify and store identified sensitive data in a database.
List and delete sensitive data records.
Deployable with Docker and Docker Compose.
Comprehensive testing using Pytest.


Prerequisites
Python 3.9 or higher
Flask and required dependencies (requirements.txt)
Docker (optional)


Installation
1.Clone the repository:
git clone https://github.com/your-username/sensitive-data-scanner.git  
cd sensitive-data-scanner  
2.Install Python dependencies:
pip install -r requirements.txt  
Ensure the uploads/ folder exists in the project directory for uploaded files.

Command	Description
Run the application locally:" python app.py	"
Run the application in Docker:" docker compose up --build "	
Run test cases:pytest test_app.py	
Access the application at http://127.0.0.1:8080.  (port as specified in code)


Testing
Run the tests using Pytest:
  
Deployment
The application has been deployed on Render. You can access it at:
https://aurva-app.onrender.com/

Database Schema  
 Table 1: `carrots`  
| Column         | Type      | Description                     |  
|----------------|-----------|---------------------------------|  
| `id`           | INTEGER   | Primary key.                   |  
| `filename`     | STRING    | Name of the uploaded file.     |  
| `upload_time`  | DATETIME  | Time when the file was uploaded.|  

Table 2: `potatoes`  
| Column            | Type      | Description                              |  
|-------------------|-----------|------------------------------------------|  
| `id`              | INTEGER   | Primary key.                            |  
| `carrot_id`       | INTEGER   | Foreign key linking to `carrots.id`.    |  
| `sensitive_data`  | STRING    | Classified sensitive data.              |  
| `classification`  | STRING    | Type of the sensitive data (e.g., PAN). |  


