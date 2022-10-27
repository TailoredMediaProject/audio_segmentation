FROM inaspeechseg

# install Java
ENV PATH=$PATH:/opt/java/jdk-15.0.2/bin

RUN mkdir /opt/java && \
    curl https://download.java.net/java/GA/jdk15.0.2/0d1cfde4252546c6931946de8db48ee2/7/GPL/openjdk-15.0.2_linux-x64_bin.tar.gz | tar -xz -C /opt/java/

# install LIUM

RUN mkdir /lium
COPY LIUM_SpkDiarization-8.4.1.jar /lium/LIUM_SpkDiarization-8.4.1.jar

# install wrapper and visualisation code

RUN mkdir /inaSpeechSegmenter/segwrapper
RUN mkdir /results

COPY segwrapper.py /inaSpeechSegmenter/segwrapper
COPY merge_visualise.py /inaSpeechSegmenter/segwrapper
COPY test_wrapper.ipynb /inaSpeechSegmenter

RUN rm /inaSpeechSegmenter/API_Tutorial.ipynb

# start Jupyter

WORKDIR /inaSpeechSegmenter

CMD /bin/bash -c "source /etc/bash.bashrc && jupyter notebook --notebook-dir=/inaSpeechSegmenter --ip 0.0.0.0 --no-browser --allow-root"
