# get INA speech segmenter
git clone https://github.com/ina-foss/inaSpeechSegmenter.git


#build INA speech segmenter docker
cd inaSpeechSegmenter
docker build -t inaspeechseg .
cd ..

# get LIUM diarisation
wget https://git-lium.univ-lemans.fr/Meignier/lium-spkdiarization/blob/master/jar/lium_spkdiarization-8.4.1.jar.gz
gunzip lium_spkdiarization-8.4.1.jar.gz


# build combined docker
docker build -t audioseg .


