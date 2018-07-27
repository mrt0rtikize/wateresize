FROM alpine:latest

RUN apk add --no-cache python3 imagemagick6 git 
RUN pip3 install --upgrade pip && pip3 install Wand
RUN git clone --single-branch -b develop https://github.com/mrt0rtikize/wateresize.git 
RUN mkdir /wateresize/images

VOLUME ["/images"]

WORKDIR /wateresize

ENTRYPOINT ["/wateresize/entrypoint.sh"]

