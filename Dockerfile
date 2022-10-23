FROM linuxserver/webtop:ubuntu-xfce

WORKDIR /tmp

COPY sources.list /etc/apt/sources.list

RUN apt-get update \
    && apt-get install -y zip python3-pip wget fonts-liberation libnspr4 libnss3 xdg-utils \
    && wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i google-chrome-stable_current_amd64.deb \
    && pip install selenium requests pillow beautifulsoup4

COPY . /app

