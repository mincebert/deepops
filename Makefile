.PHONY: all
all: deepops

.PHONY: remake
remake: clean all

.PHONY: deepops
deepops:
	./setup.py sdist bdist_wheel

.PHONY: upload
upload:
	python3 -m twine upload dist/*

.PHONY: clean
clean:
	rm -rf build dist deepops.egg-info

.PHONY: test_deepops
test_deepops:
	python3 -m test_deepops