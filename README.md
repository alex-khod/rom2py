# 🐉 rom2py
Rage of Mages 2 (ROM) implementation in python/opengl.

# Current state:
Can draw a bunch of animations...

# Dependencies
Requires Python 3.7x.
```
git clone https://github.com/alex-khod/rom2py.git
cd rom2py
pip install -r requirements.txt
python setup.py build
```

Requires ROM2 to be installed to run. Pinpoint the path containig `graphics.res` in `config.ini`.
# Running stuff
* Main - `python main.py`
* Tests - `python -m "nose" tests`
* Benchmarks `python -m "nose" time_tests --with-timer`

See makefile for more commands.
See [rom2books](https://github.com/alex-khod/rom2books) repo for more hijinks with ROM2 assets.
