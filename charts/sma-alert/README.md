# sma-alert

Get data from kubeweekly and create Weekly CRDs based on community-operator and push to git datastore

## Installing the Chart

To install the chart with the release name `my-release` and secret `foo`:

```console
kubectl apply -f secret.yaml

helm repo add zufardhiyaulhaq https://charts.zufardhiyaulhaq.com/
helm install sma-alert zufardhiyaulhaq/sma-alert --values values.yaml --set secret=foo
```

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| cronSchedule | string | `"0 12 * * 1-5"` |  |
| image.repository | string | `"zufardhiyaulhaq/sma-alert"` |  |
| image.tag | string | `"v1.0.0"` |  |
| secret | string | `""` |  |
| weekly.community | string | `"Cloud Native Indonesia Community"` |  |
| weekly.image_url | string | `"https://raw.githubusercontent.com/cncf/artwork/master/other/cncf/horizontal/color/cncf-color.png"` |  |
| weekly.namespace | string | `"kubernetes-community"` |  |
| weekly.tags | string | `"weekly,kubernetes"` |  |

