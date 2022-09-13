.PHONY: helm.create.releases
helm.create.releases:
	helm package charts/sma-alert --destination charts/releases
	helm repo index charts/releases
