book:
	python -m jupyterlab
dependencies:
    pip install -r requirements.txt
tests:
    python -m "nose" tests
benchmarks:
    python -m "nose" time_tests --with-timer
build:
    # build cython extensions, non essential
    python setup.py build_ext --inplace
start:
    python main.py
fetch formats:
    git clone https://github.com/alex-khod/orom-file-formats.git src/formats/orom-file-formats
test data:
    python tests\data.py