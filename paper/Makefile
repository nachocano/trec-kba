NAME=summer_research_paper
DOC=summer_research_paper

all: compile clean
compile: $(DOC).tex
	pdflatex $(DOC).tex
	bibtex $(DOC)
	pdflatex $(DOC).tex
	pdflatex $(DOC).tex
clean:
	rm *.aux *.log *.bbl *.blg
