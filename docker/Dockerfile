FROM postgres:14

# Set the timezone to East Africa Time (EAT)
ENV TZ=Africa/Nairobi

# Copy the initialization script to the Docker container
COPY init.sql /docker-entrypoint-initdb.d/

EXPOSE 5432
