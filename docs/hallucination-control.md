# Control de alucinaciones

## Punto clave

No existe garantia absoluta de alucinaciones `0`. Lo correcto es diseñar para:

- maximizar grounding,
- minimizar invencion,
- abstenerse cuando no haya soporte,
- escalar a humano en alto riesgo.

## Medidas implementadas

- RAG hibrido lexical + semantico.
- Citas devueltas al cliente.
- Prompt de grounding estricto.
- Politica de abstencion si no hay soporte suficiente.
- Restricciones por perfil de dominio.

## Medidas recomendadas a continuacion

- reranker dedicado,
- verificador secundario,
- golden set por dominio,
- evaluacion automatica nocturna,
- score de confianza con umbrales por caso de uso,
- bloqueo de respuestas sin fuente en intents factuales.
