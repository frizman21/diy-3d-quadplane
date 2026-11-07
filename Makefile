# Everything runs inside the container. Nothing is installed on the host.
RUN = docker compose run --rm cad

.PHONY: image lock shell build test viewer clean

image:            ## build the CAD container (rerun after changing dependencies)
	docker compose build

lock:             ## refresh uv.lock after editing pyproject.toml, then `make image`
	$(RUN) uv lock

shell:            ## interactive shell inside the container
	$(RUN) bash

build:            ## export every part to build/ (STL + STEP)
	$(RUN) python scripts/build_all.py $(PART)

test:             ## run checks (fit on the print bed, valid solids)
	$(RUN) pytest -q

viewer:           ## 3D viewer at http://localhost:3939
	docker compose run --rm --service-ports cad python -m ocp_vscode --host 0.0.0.0 --port 3939

clean:
	rm -rf build/*
