aria2c --enable-rpc --check-certificate=false \
   --max-connection-per-server=8 --rpc-max-request-size=512M \
   --bt-stop-timeout=1200 --min-split-size=10M --follow-torrent=mem --split=10 \
   --daemon=true --allow-overwrite=true --max-overall-download-limit=0 \
   --max-overall-upload-limit=1K --max-concurrent-downloads=15 --continue=true \
   --peer-id-prefix=-qB4360- --user-agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15' --peer-agent=qBittorrent/4.3.6 \
   --disk-cache=64M --bt-enable-lpd=true --seed-time=0 --max-file-not-found=0 \
   --max-tries=20 --auto-file-renaming=true --reuse-uri=true --http-accept-gzip=true \
   --content-disposition-default-utf8=true --netrc-path=/usr/src/app/.netrc
