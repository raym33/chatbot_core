# MCP Connector Templates

Los `mcps/` definen contratos de integracion para datos vivos y acciones reales. La regla de producto es sencilla:

- `skills/` define como debe comportarse el chatbot.
- `data/corpus/` contiene conocimiento fijo versionado.
- `mcps/` conecta con sistemas vivos: CRM, ERP, citas, documentos, HIS, seguros, OCR, GIS y ticketing.

## Contrato minimo

Cada conector debe declarar:

- herramientas disponibles,
- variables de entorno requeridas,
- clasificacion de datos,
- permisos necesarios,
- politica de auditoria,
- limites anti-abuso.

## Seguridad

Ningun MCP debe exponer datos personales sin autenticacion, autorizacion, minimizacion y trazabilidad. Los conectores deben devolver resultados estructurados y nunca instrucciones ocultas que puedan contaminar el prompt.
