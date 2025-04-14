# Define the pip freeze command depending on the OS
ifeq ($(OS),Windows_NT)
    RM = del /f
	RMDIR = rmdir /s /q
else
    RM = rm -rf
	RMDIR = rm -rf
endif

# Define the pip freeze command depending on the OS
# Default target
all: requirements.txt

# Generate requirements.txt from pip freeze
freeze:
	python scripts/freeze_clean.py

uninstall:
	pip freeze > installed.txt
	pip uninstall -y -r installed.txt
	$(RM) installed.txt

install:
	pip install -r requirements.txt
	$(RMDIR) mincal.egg-info

download_matches:
	python scripts/download_matches.py

download_match_data:
	python scripts/download_match_data.py