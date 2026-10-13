FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b \
    fonts-liberation fonts-dejavu-core fonts-noto-cjk fonts-noto-core \
    fonts-urw-base35 fonts-inconsolata \
    && rm -rf /var/lib/apt/lists/*

# Ubuntu Mono is the code font O'Reilly stylesheets ask for. Debian does not
# package it, so it is fetched from a pinned commit of Google Fonts.
ARG UBUNTU_MONO_URL=https://raw.githubusercontent.com/google/fonts/81e687fb3c5344bb18a4bfc74897ee7bd1c05afa/ufl/ubuntumono
ADD --chmod=644 \
    ${UBUNTU_MONO_URL}/UbuntuMono-Regular.ttf \
    ${UBUNTU_MONO_URL}/UbuntuMono-Bold.ttf \
    ${UBUNTU_MONO_URL}/UbuntuMono-Italic.ttf \
    ${UBUNTU_MONO_URL}/UbuntuMono-BoldItalic.ttf \
    /usr/share/fonts/truetype/ubuntu/

# Map the font names books use onto the fonts installed above.
COPY docker/fonts.conf /etc/fonts/local.conf
RUN fc-cache -f

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8000
CMD ["python", "main.py", "--host", "0.0.0.0"]
