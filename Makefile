all: deepops

.PHONY: remake deepops upload clean


remake: clean all

deepops:
	./setup.py sdist bdist_wheel

upload:
	python3 -m twine upload dist/*

clean:
	rm -rf build dist deepops.egg-info
