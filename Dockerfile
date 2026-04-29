# Stage 1: builder — installs dependencies
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: final image — lean runtime
FROM python:3.11-slim
WORKDIR /app

# Create a non-root user (security requirement)
RUN useradd -m -u 1000 appuser

# Copy installed packages from builder stage
COPY --from=builder /root/.local /home/appuser/.local

COPY . .
RUN chown -R appuser /app

USER appuser
ENV PATH=/home/appuser/.local/bin:$PATH

EXPOSE 7860
CMD ["python", "-m", "flask", "--app", "noshow_iq.api", "run", "--host", "0.0.0.0", "--port", "7860"]