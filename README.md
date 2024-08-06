# Nfinity backend

## Overview

This project comprises a backend API, a provider API gateway, and a PostgreSQL database configured using Docker Compose. The backend API is FastAPI-based, and the provider API interacts with external Replicate service.

## Prerequisites

- Docker installed on your machine.
- Docker Compose installed on your machine.

## Installation

1. Clone the repository:
    ```sh
    git clone git@github.com:nfinityai/nfinityai-backend.git
    cd nfinityai-backend
    ```

2. Create a `.env` file in the root directory of the project and define the following environment variables:
    ```dotenv
    # Backend API Environment Variables
    BACKEND_API_PORT=8000
    BACKEND_API_SECRET_KEY=your_secret_key
    BACKEND_API_JWT_SECRET=your_jwt_secret
    POSTGRES_USER=your_postgres_user
    POSTGRES_PASSWORD=your_postgres_password
    POSTGRES_DB=your_postgres_db
    POSTGRES_HOST=db
    BACKEND_API_ADMIN_USERNAME=your_admin_username
    BACKEND_API_ADMIN_PASSWORD=your_admin_password
    BACKEND_API_INFURA_BASE_URL=your_infura_base_url_with_api_key
    BACKEND_API_CONTRACT_ADDRESS=0x3ABd9c3518b475fd369ad546d81475014dfda84c  # Nfinity contract address
    BACKEND_API_COINGECKO_API_KEY=your_coingecko_api_key
   
   BACKEND_API_ETHERSCAN_API_KEY=your_etherscan_api_key
   BACKEND_API_NFNT_CONTRACT_ADDRESS=0x82d36570842fc1ac2a3b4dbe0e7c5c0e2e665090  # Nfnt contract etherscan address

    # Provider API Gateway Environment Variable
    PROVIDER_REPLICATE_API_TOKEN=your_provider_replicate_api_token
    ```

3. Start the services:
    ```sh
    docker-compose up --build
    ```

4. Apply Alembic migrations to set up the database:
    ###### Open a new terminal and navigate to the project directory
    ```sh
    docker-compose exec backend-api alembic upgrade head
    ```

## Usage

To start the services, navigate to the project directory and run:

```sh
docker-compose up --build
