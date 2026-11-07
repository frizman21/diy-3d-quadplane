# Everything runs inside the container. Nothing is installed on the host.
RUN = docker compose run --rm cad
ANALYSIS_REST = python -m analysis.a2_sizing && python -m analysis.a4_stability && python -m analysis.a3_propulsion \
	&& python -m analysis.a4_stability && python -m analysis.a5_performance && python -m analysis.a6_structures

.PHONY: image lock shell build test viewer clean analysis analysis-fast

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

analysis:         ## full engineering analysis chain (airfoils -> sizing -> stability -> propulsion -> performance -> structures)
	$(RUN) bash -c "python -m analysis.a1_airfoils && $(ANALYSIS_REST)"

analysis-fast:    ## same, skipping the (slow) airfoil XFOIL sweep
	$(RUN) bash -c "$(ANALYSIS_REST)"

viewer:           ## 3D viewer at http://localhost:3939
	docker compose run --rm --service-ports cad python -m ocp_vscode --host 0.0.0.0 --port 3939

clean:
	rm -rf build/*
