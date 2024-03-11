# Library Management System Using FASTAPI

This is a simple library management system's api created using FastAPI for the endpoint, SQLAlchemy for ORM and PostgreSQL for the backend database.

## How to run this code?

1. Create a .env file
 The file must follow this format

   ```bash
   host=database_host
   database=database_name
   user=database_username
   password=database_password
   secret=AccessToken_secret_key
   algorithm=Token_algorithm
   secret_refresh = RefreshToken_secret_key
   ```

2. Install requirements

   Run `pip install -r requirements.txt`

3. Run the script

   Run the script with `uvicorn main:app --reload`

   The `--reload` flag as the name suggest will watch your file for change and reload the endpoint. One of the important flag is `--host 0.0.0.0` that will host the endpoint to your local ip.

## Docs

   To know more about the endpoint and expected format you can got to `localhost/docs`(that is if you are hosting the api in your localhost)
   You can use thos swaager API docs to test the api.
