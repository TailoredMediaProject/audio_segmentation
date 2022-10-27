# Audio segmentation toolchain

Toolchain to segment and cluster audio programmes.

The toolchain is built using [INA Speech Segmenter](https://github.com/ina-foss/inaSpeechSegmenter) and [LIUM Speaker Diarization](https://projets-lium.univ-lemans.fr/spkdiarization/). 

# Usage

The toolchain is deployed as a Docker container, which provides a Jupyter notebook as UI. The toolchain can be started from a provided notebook, and writes results to a mounted folder.

## Build

Prequisites:
- NVIDIA CUDA driver installed on host system (not required during build, but at runtime)
- Docker installation with GPU support
- git and wget installed

Running ```build.sh``` will fetch sources and prebuilt binaries, build first the INA Speech Segmenter container, and the Audio Segmentation container on top of it. By default, the resulting container will be labelled ```audioseg```.
 
## Run

When starting the container, the media file directory and the result directory 


# Acknowledgement

<img src="img/Tailored_Media_Logo_Final.png" width="200">

The research leading to these results has been funded partially by the program ICT of the Future by the Austrian Federal Ministry of Climate Action, Environment, Energy, Mobility, Innovation and Technology (BMK) in the project [TailoredMedia](https://www.joanneum.at/en/digital/reference-projects/tailoredmedia). 

<img src="img/BMK_Logo_srgb.png" width="100"><img src="img/FFG_Logo_DE_RGB_1000px.png" width="100">
