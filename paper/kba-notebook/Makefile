NAME=kba-notebook
DOC=kba-notebook

all: compile clean
compile: $(DOC).tex
	pdflatex $(DOC).tex
	bibtex $(DOC)
	pdflatex $(DOC).tex
	pdflatex $(DOC).tex
clean:
	rm *.aux *.log *.bbl *.blg
