from setuptools import setup, find_packages

setup(
    name="branch-loans-api",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "sqlalchemy>=1.4.0",
        "alembic>=1.7.0",
        "pydantic>=1.8.0",
        "python-multipart>=0.0.5",
        "psycopg2-binary>=2.9.0",
    ],
    extras_require={
        "test": [
            "pytest>=6.0.0",
            "pytest-cov>=2.0.0",
            "httpx>=0.19.0",
        ],
    },
)
