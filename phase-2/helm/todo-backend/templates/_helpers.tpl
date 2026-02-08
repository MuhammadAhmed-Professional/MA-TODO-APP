{{/*
Expand the name of the chart.
*/}}
{{- define "todo-backend.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "todo-backend.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "todo-backend.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "todo-backend.labels" -}}
helm.sh/chart: {{ include "todo-backend.chart" . }}
{{ include "todo-backend.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "todo-backend.selectorLabels" -}}
app.kubernetes.io/name: {{ include "todo-backend.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "todo-backend.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "todo-backend.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Dapr annotations
*/}}
{{- define "todo-backend.daprAnnotations" -}}
{{- if .Values.dapr.enabled }}
dapr.io/enabled: "true"
dapr.io/app-id: {{ .Values.dapr.appId | quote }}
dapr.io/app-port: {{ .Values.dapr.appPort | quote }}
dapr.io/app-protocol: {{ .Values.dapr.appProtocol | quote }}
{{- if .Values.dapr.enableMetrics }}
dapr.io/enable-metrics: "true"
dapr.io/metrics-port: {{ .Values.dapr.metricsPort | quote }}
{{- end }}
{{- if .Values.dapr.config }}
dapr.io/config: {{ .Values.dapr.config | quote }}
{{- end }}
{{- end }}
{{- end }}
