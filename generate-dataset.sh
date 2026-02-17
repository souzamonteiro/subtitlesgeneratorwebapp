#!/bin/bash

# This script generates the dataset files for the web app. It should be run from the project root.
mkdir -p dataset

/opt/homebrew/bin/espeak -v en "Hello, this is a test" -w dataset/english_test.wav
/opt/homebrew/bin/espeak -v es "Hola, esto es una prueba" -w dataset/spanish_test.wav
/opt/homebrew/bin/espeak -v pt "Olá, isto é um teste" -w dataset/portuguese_test.wav