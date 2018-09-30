# GNU Makefile for acycliCode 
# Author: Marios Papachristou
# Usage: 
# - make to prepare for installation
# - make install for installation

# Copyright (c) 2018 Marios Papachristou

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# apt-get install command
APT_INSTALL_Y=apt-get install -y 

# destination to symlink acyclicode
INSTALL_PREFIX=/usr/local/bin

# Currend working directory
CURRENT_DIR = $(shell pwd)

default: 
	apt-get update
	$(APT_INSTALL_Y) cflow python3

install: src/helpers.py src/acyclicode.py src/git_commits.py
	ln -s $(CURRENT_DIR)/src/acyclicode.py $(INSTALL_PREFIX)/acyclicode
	chmod +x $(INSTALL_PREFIX)/acyclicode

uninstall: $(INSTALL_PREFIX)/acyclicode  
	rm $(INSTALL_PREFIX)/acyclicode  
 
test:
	cd tests && $(MAKE)

