# ![RealWorld Example App](logo.png)

> ### Python + Flask + Couchbase codebase containing real world examples (CRUD, auth, advanced patterns, etc) that adheres to the [RealWorld](https://github.com/gothinkster/realworld) spec and API.


### [Demo](https://demo.realworld.io/)&nbsp;&nbsp;&nbsp;&nbsp;[RealWorld](https://github.com/gothinkster/realworld)


This codebase was created to demonstrate a fully fledged fullstack application built with Python + Flask + Couchbase including CRUD operations, authentication, routing, pagination, and more.

We've gone to great lengths to adhere to the Flask community styleguides & best practices.

For more information on how to this works with other frontends/backends, head over to the [RealWorld](https://github.com/gothinkster/realworld) repo.


# How it works

> All the routes are defined in the routes/v1 directory, and their models are implemented in the models folder.

# Getting started

## Prepare the environment

1. Navigate to the realworld directory and create a new file called `.env`.
2. Add the following to the content:
   ```
   DB_CONNECTION_STRING = 
   DB_USERNAME = 
   DB_PASSWORD = 
   SECRET_KEY = 
   ```
3. Fill in your specific Couchbase database credentials.
   
## Running the application

1. `poetry install`
2. `poetry run python realworld/app.py`

