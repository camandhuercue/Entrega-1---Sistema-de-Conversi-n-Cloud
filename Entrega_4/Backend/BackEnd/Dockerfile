FROM us-central1-docker.pkg.dev/soluciones-cloud/backend/backend_base:backend_base
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "compress_api:create_app()"]
