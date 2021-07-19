FROM narima/megaria:latest

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app

RUN pip uninstall yt-dlp -y \
    && pip install --no-cache-dir youtube-dl \
    
COPY extract /usr/local/bin
COPY pextract /usr/local/bin
RUN chmod +x /usr/local/bin/extract && chmod +x /usr/local/bin/pextract
COPY . .
COPY .netrc /root/.netrc
RUN chmod 600 /usr/src/app/.netrc
RUN chmod +x aria.sh

CMD ["bash","start.sh"]
