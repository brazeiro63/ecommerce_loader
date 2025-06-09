FROM python:3.11-slim

# Instala dependências do sistema para Playwright
RUN apt-get update && \
    apt-get install -y wget gnupg2 ca-certificates curl \
    fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 \
    libatk1.0-0 libcups2 libdbus-1-3 libgdk-pixbuf2.0-0 \
    libnspr4 libnss3 libx11-xcb1 libxcomposite1 libxdamage1 \
    libxrandr2 xdg-utils libu2f-udev libvulkan1 \
    libxcb1 libxext6 libxfixes3 libxi6 libxtst6 \
    lsb-release && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /

COPY . .

RUN pip install --upgrade pip

# Instale playwright explicitamente antes do requirements.txt (ou depois, mas SEMPRE antes do install dos browsers)
RUN pip install playwright

RUN pip install -r requirements.txt

RUN python -m playwright install --with-deps

EXPOSE 8002

# CMD ["python", "-m", "backend/main.py"]
# ou para FastAPI
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8002"]
