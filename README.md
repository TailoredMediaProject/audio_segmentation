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

### Starting the container

To run the container, execute ```run.sh```. You may need to make the following adjustments to this script:
- source media folder on host maching (to be mounted as volume into the container)
- folder to store results on host machine (to be mounted as volume into the container)
- the port number on the host machine (in case the default 8888 is already taken)

After starting up the container will print the URL to connect to the Jupyter notebook in the browser. Alternatively, you can open http://<host>:<port> in your browser and enter the token printed on the command line.

### Running the segmenter 

The notebook defines a ```mediafiles``` list with the filenames of the media files in the source folder. This list needs to be adjusted to the files present.

The algorithm uses a set of default parameters. Those can be initialised by calling ```segwrapper.get_default_params()```, which returns a dictionary with the parameters. A parameter set can be printed using ```segwrapper.print_params(params)```. Parameters can be modified by changing the respective value in the dictionary.

```segwrapper.segment_plot``` calls the entire pipeline, and puts result CSV files and plots into the result folder.


# Acknowledgement

<img src="img/Tailored_Media_Logo_Final.png" width="200">

The research leading to these results has been funded partially by the program ICT of the Future by the Austrian Federal Ministry of Climate Action, Environment, Energy, Mobility, Innovation and Technology (BMK) in the project [TailoredMedia](https://www.joanneum.at/en/digital/reference-projects/tailoredmedia). 

<img src="img/BMK_Logo_srgb.png" width="100"><img src="img/FFG_Logo_DE_RGB_1000px.png" width="100">
