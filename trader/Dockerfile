FROM python:3.5
ENV PROJECT_DIR=trader
RUN mkdir ${PROJECT_DIR}
WORKDIR /${PROJECT_DIR}
ADD . ./

# talib installation
RUN wget "https://netcologne.dl.sourceforge.net/project/ta-lib/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz"
RUN tar -xvzf ta-lib-0.4.0-src.tar.gz
WORKDIR ta-lib
RUN ./configure --prefix=/usr
RUN make
RUN make install
ENV LD_LIBRARY_PATH="/usr/lib:$LD_LIBRARY_PATH"
# -----------------
WORKDIR /${PROJECT_DIR}
RUN pip install -r requirements.txt
EXPOSE 80
#RUN python -m aiohttp.web -H localhost -P 80 start:start_server
