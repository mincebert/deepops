all: deepops

.PHONY: remake deepops upload clean tests


remake: clean all

deepops:
	./setup.py sdist bdist_wheel

upload:
	python3 -m twine upload dist/*

clean:
	rm -rf build dist deepops.egg-info

tests:
	python3 tests/test_deepops.py