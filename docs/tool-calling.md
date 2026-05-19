# Tool calling

## Objetivo

El chatbot core separa conocimiento documental de datos operativos. Los documentos explican politicas, procesos y requisitos. Las herramientas consultan o preparan acciones.

## Herramientas incluidas

- `appointment.availability`: huecos simulados para cita, demo, admision o reserva.
- `incident.create`: prepara ticket trazable.
- `handoff.create`: prepara derivacion humana.

## Endpoints

```bash
curl http://127.0.0.1:8000/v1/tools
```

```bash
curl -X POST http://127.0.0.1:8000/v1/tools/invoke \
  -H 'Content-Type: application/json' \
  -d '{"name":"appointment.availability","arguments":{"service":"demo"}}'
```

## Integracion real

En produccion, cada herramienta debe sustituir su simulacion por un adaptador:

- hospital: HIS, agenda, admision, CRM sanitario.
- ayuntamiento: cita previa, incidencias, sede electronica.
- empresa: CRM, ticketing, ERP, facturacion.
