# Anexo multimodal: STT, TTS y OCR

## STT open source

| Motor | Uso recomendado | Notas |
|---|---|---|
| Whisper / faster-whisper | Transcripcion multilingue general | Muy robusto, buena base para telefonia y notas de voz |
| whisper.cpp | Edge y CPU/Metal | Facil de desplegar cerca del usuario |
| Vosk | Telefonia ligera offline | Menor coste, menor calidad general que Whisper |

## TTS open source

| Motor | Uso recomendado | Notas |
|---|---|---|
| Piper | TTS local rapido | Buen equilibrio para voz institucional offline |
| Coqui XTTS | Voces mas naturales y clonacion controlada | Revisar licencia/modelos y consentimiento de voces |
| Kokoro / modelos ligeros | Lectura rapida y coste bajo | Util para respuestas cortas |

## OCR open source

| Motor | Uso recomendado | Notas |
|---|---|---|
| Tesseract | OCR clasico, formularios simples | Maduro y portable |
| PaddleOCR | Documentos, tablas y OCR multilingue | Mejor para pipeline documental moderno |
| Surya OCR | Layout y documentos complejos | Util en PDFs escaneados y documentos administrativos |

## Pipeline recomendado

1. OCR/STT convierte entrada a texto.
2. Clasificador detecta PII y riesgo.
3. RAG recupera fuentes.
4. LLM responde con citas.
5. TTS lee solo respuestas aprobadas por el verificador.

## Seguridad multimodal

- No ejecutar instrucciones extraidas de imagen/audio como instrucciones del sistema.
- Tratar OCR/STT como contenido de usuario no confiable.
- Redactar PII antes de indexar.
- Mantener trazabilidad de archivo, hash, fecha y fuente.
