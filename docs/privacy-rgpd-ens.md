# Privacidad, RGPD, LOPDGDD y ENS

## Estado implementado

El core incorpora una base tecnica inicial para privacidad por diseno:

- Redaccion de PII antes de persistir mensajes.
- Redaccion de comentarios de feedback.
- Redaccion de motivos de escalado.
- Exportacion de datos de una sesion.
- Supresion completa de una sesion.
- Anonimizacion de una sesion.
- Purga por retencion.

## PII detectada

| Tipo | Ejemplo |
|---|---|
| Email | `usuario@example.com` |
| Telefono ES | `612345678` |
| DNI/NIE | `12345678Z`, `X1234567L` |
| IBAN ES | `ES91...` |
| Tarjeta bancaria | Secuencias compatibles |
| Direccion postal | Calle, avenida, plaza, paseo |
| Historia clinica | NHC, numero de historia |

## Endpoints

```bash
POST /v1/privacy/scan
GET /v1/privacy/sessions/{session_id}/export
DELETE /v1/privacy/sessions/{session_id}
POST /v1/privacy/sessions/{session_id}/anonymize
POST /v1/admin/privacy/purge
```

## Variables

| Variable | Valor por defecto | Uso |
|---|---:|---|
| `MUNIBOT_REDACT_PII` | `true` | Redacta PII antes de persistir |
| `MUNIBOT_RETAIN_CONVERSATIONS_DAYS` | `30` | Retencion de mensajes y feedback |
| `MUNIBOT_RETAIN_ESCALATIONS_DAYS` | `90` | Retencion de escalados |

## Pendiente para produccion

- Base juridica y registro de actividad de tratamiento.
- Informacion al usuario y consentimiento cuando aplique.
- DPIA/EIPD para hospital, servicios sociales, seguridad o datos sensibles.
- Cifrado en reposo con gestion de claves.
- Autenticacion y autorizacion de endpoints de privacidad.
- Auditoria inmutable de accesos administrativos.
- Politica de encargados de tratamiento si hay cloud o terceros.
- Clasificacion ENS y medidas por categoria.
- Procedimiento formal para derechos RGPD.

## Recomendacion

Esta capa reduce riesgo tecnico, pero no sustituye revision legal. Para despliegues reales debe validarse con DPD/DPO, seguridad, juridico y responsables del tratamiento.
