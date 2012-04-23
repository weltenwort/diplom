#!/bin/sh

pdflatex -halt-on-error thesis.tex
biber thesis
pdflatex -halt-on-error thesis.tex
