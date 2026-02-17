#!/bin/sh

# Generate models for the application

cd models

# Get small models for English, Spanish and Portuguese languages

# English models
rm vosk-model-small-en-us-0.15.zip
rm vosk-model-small-en-us-0.15.tar.gz
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
mv vosk-model-small-en-us-0.15 model
COPYFILE_DISABLE=1 tar --format=ustar -czf vosk-model-small-en-us-0.15.tar.gz model
rm -rf model

# Spanish models
rm vosk-model-small-es-0.42.zip
rm vosk-model-small-es-0.42.tar.gz
wget https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip
unzip vosk-model-small-es-0.42.zip
mv vosk-model-small-es-0.42 model
COPYFILE_DISABLE=1 tar --format=ustar -czf vosk-model-small-es-0.42.tar.gz model
rm -rf model

# Portuguese models
rm vosk-model-small-pt-0.3.zip
rm vosk-model-small-pt-0.3.tar.gz
wget https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip
unzip vosk-model-small-pt-0.3.zip
mv vosk-model-small-pt-0.3 model
COPYFILE_DISABLE=1 tar --format=ustar -czf vosk-model-small-pt-0.3.tar.gz model
rm -rf model
