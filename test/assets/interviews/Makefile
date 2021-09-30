
test: develop
	if [[ -e tox.ini ]]; then \
	  venv/bin/tox; \
	elif [[ -e setup.py ]]; then \
	  VAULT_ADDR= venv/bin/python setup.py test; \
	fi

venv: venv/bin/activate ## Build virtual environment

format: venv/bin/black --line-length 79 --quiet --exclude '/(\.direnv|\.eggs|\.git|\.hg|\.mypy_cache|\.nox|\.tox|\.venv|\.svn|_build|buck-out|build|dist|venv|proto)/' .

venv/bin/activate: $(wildcard requirements.txt) $(wildcard setup.py)
	if [ ! -d venv ]; then \
	    virtualenv --no-download -p python3 venv; \
	fi
	venv/bin/pip install setuptools==1.4.3 lazy-object-proxy; \
	venv/bin/pip install -e .; \
	touch $@