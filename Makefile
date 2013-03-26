#
# Makefile for Ircbot
# 
# Copyright (C) 2013 Juha Autero <jautero@iki.fi>
#

PYTHON_FILES := $(wildcard *.py)

FILES:= $(PYTHON_FILES) Makefile
    
INSTALLDIR := /usr/share/ircbot
install: $(PYTHON_FILES)
	mkdir -p $(INSTALLDIR)
	cp $(PYTHON_FILES) $(INSTALLDIR)

ircbot.tar.gz: $(FILES)
	tar cvzf $@ $(FILES)