
test: develop
	if [[ -e tox.ini ]]; then \
	  venv/bin/tox; \
	elif [[ -e setup.py ]]; then \
	  VAULT_ADDR= venv/bin/python setup.py test; \
	fi

venv: venv/bin/activate ## Build virtual environment

venv/bin/activate: $(wildcard requirements.txt) $(wildcard setup.py)
	if [ ! -d venv ]; then \
	    virtualenv --no-download -p python3 venv; \
	fi
	venv/bin/pip install setuptools==1.4.3 lazy-object-proxy; \
	venv/bin/pip install -e .; \
	# if [[ -e requirements.txt ]]; then \
	#     venv/bin/pip install -r requirements.txt; \
	# fi
	touch $@