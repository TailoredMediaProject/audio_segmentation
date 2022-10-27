sudo docker run --gpus 0 -v /home/baw/data/audio_segmentation/mediathek_content:/inaSpeechSegmenter/media -v /home/baw/audio_segmentation/results/:/results -it -p 9882:8888 audioseg

