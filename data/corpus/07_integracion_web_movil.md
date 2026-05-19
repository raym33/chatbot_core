# 7. INTEGRACIÓN EN WEB Y APLICACIÓN MÓVIL

## 7.1 Estrategia multicanal

El chatbot se concibe como un **servicio único** consumido por dos canales nativos del ayuntamiento. Toda la lógica conversacional, RAG, modelos y herramientas reside en el backend; los canales son clientes finos que aportan presentación, captura multimedia y notificaciones.

```
Ciudadano ─► Widget web (sede / portal) ─┐
                                          ├─► API conversacional /chat/v1
Ciudadano ─► App iOS/Android oficial ────┘       (WebSocket + REST)
```

## 7.2 Widget web

### 7.2.1 Características
- Web Component nativo `<munibot-widget>` distribuido vía CDN interno del ayuntamiento.
- Carga **diferida** (1,8 KB de bootstrap + 32 KB del componente bajo demanda).
- **Shadow DOM** para aislamiento CSS y resistencia a estilos de la página anfitriona.
- **Sin cookies de terceros**: identidad de sesión por `sessionStorage` + JWT corto.
- Burbuja flotante en esquina inferior derecha, abierta o cerrada según política del sitio.
- Soporte total **modo oscuro**, **alto contraste**, **tamaño de texto +/-**.

### 7.2.2 Snippet de integración

```html
<!-- En cualquier página del portal o sede electrónica -->
<script src="https://chat.ayto.gob.es/munibot.js" defer></script>
<munibot-widget
  tenant="ayuntamiento"
  locale="es-ES"
  context-url
  channel="sede"
  position="bottom-right"
  accent="#0a3d62"
  privacy-url="/aviso-legal#chatbot">
</munibot-widget>
```

El atributo `context-url` envía solo la URL actual (no su contenido) para que el chatbot tenga contexto de la página en la que se ha abierto.

### 7.2.3 Eventos JavaScript
```js
const widget = document.querySelector('munibot-widget');
widget.addEventListener('munibot:opened', e => analytics.track('chat_open'));
widget.addEventListener('munibot:resolved', e => analytics.track('chat_resolved', e.detail));
widget.addEventListener('munibot:escalated', e => analytics.track('chat_escalated', e.detail));
widget.open({ message: 'Quiero pedir cita en padrón' }); // apertura programática
```

### 7.2.4 Accesibilidad del widget
- Cumplimiento **WCAG 2.2 AA** y **EN 301 549**.
- Navegación 100 % con teclado, foco visible.
- ARIA roles `dialog`, `log`, `status`.
- Soporte de lectores de pantalla (probado con NVDA, VoiceOver, TalkBack).
- Botón "Lectura fácil" que adapta tono, vocabulario y longitud de la respuesta.
- Atajo `Alt+M` para abrir/cerrar.

## 7.3 Aplicaciones móviles

### 7.3.1 iOS

- **Lenguaje**: Swift 6, Swift Concurrency.
- **Mínimo**: iOS 16.
- **Framework**: SwiftUI con `Observation`.
- **Distribución del SDK**: Swift Package Manager privado del ayuntamiento.

```swift
import Munibot

@main
struct AppAyto: App {
    init() {
        Munibot.configure(
            endpoint: URL(string: "https://chat.ayto.gob.es")!,
            tenantId: "ayuntamiento",
            locale: .init(identifier: "es-ES")
        )
    }

    var body: some Scene {
        WindowGroup {
            MainTabView()
                .munibotFloatingButton()   // botón global
        }
    }
}
```

- Integración nativa con **Live Activities** para seguimiento de incidencias.
- **Push** vía APNS con categorías de notificación (`cita_recordatorio`, `incidencia_actualizada`).
- **Sign in with Apple** opcional para sesión persistente cifrada en Keychain.
- **App Intents** para integración con Siri y atajos: "Reportar incidencia con Munibot".

### 7.3.2 Android

- **Lenguaje**: Kotlin 2.x + Jetpack Compose Multiplatform.
- **Mínimo**: API 26 (Android 8).
- **Distribución**: módulo AAR vía repositorio Maven privado.

```kotlin
class AppAyto : Application() {
    override fun onCreate() {
        super.onCreate()
        Munibot.init(
            context = this,
            endpoint = "https://chat.ayto.gob.es",
            tenantId = "ayuntamiento",
            locale = Locale("es", "ES")
        )
    }
}
```

- **Push** vía FCM con canales segmentados.
- **Quick Settings Tile** para apertura rápida del chat.
- **App Actions** para integración con Google Assistant.
- **Biometric** (huella, cara) para sesiones persistentes.

### 7.3.3 Capacidades nativas comunes
- Cámara y galería (con compresión local antes del upload).
- Geolocalización (precisa y aproximada, según consentimiento granular).
- Reconocimiento de voz **on-device** (Apple Speech / Android SpeechRecognizer) para entrada por voz sin enviar audio a servidor.
- Síntesis de voz **on-device** para accesibilidad (TTS del sistema).
- Modo **offline reducido**: caché de 200 FAQs más frecuentes.

## 7.4 API conversacional

### 7.4.1 Protocolo
- **REST + WebSocket** sobre HTTPS.
- WebSocket para *streaming* token-a-token y eventos de "typing".
- REST para operaciones de gestión (historial, feedback, cierre).

### 7.4.2 Endpoints principales

| Método | Ruta | Función |
|---|---|---|
| POST | `/v1/sessions` | Crear sesión (devuelve `session_id` y JWT corto) |
| WS | `/v1/sessions/{id}/stream` | Canal bidireccional para mensajes |
| POST | `/v1/sessions/{id}/messages` | Enviar mensaje (no streaming) |
| GET | `/v1/sessions/{id}/history` | Historial paginado |
| POST | `/v1/sessions/{id}/escalate` | Escalado a humano |
| POST | `/v1/sessions/{id}/feedback` | Feedback (👍/👎 + texto) |
| POST | `/v1/sessions/{id}/upload` | Adjuntar imagen (presigned URL a MinIO) |
| GET | `/v1/health` | Salud pública (sin datos sensibles) |
| GET | `/v1/metrics` | Métricas Prometheus (solo red interna) |

### 7.4.3 Esquema de mensaje (JSON)

```json
{
  "id": "msg_01HXY...",
  "role": "user",
  "content": "¿Cuándo se paga el IBI?",
  "ts": "2026-05-19T11:42:13Z",
  "channel": "web",
  "locale": "es-ES",
  "attachments": [],
  "context": {
    "page_url": "https://www.ayto.gob.es/impuestos",
    "geo": { "lat": null, "lon": null, "consent": false }
  }
}
```

Respuesta en *streaming* (eventos Server-Sent):

```
event: token
data: {"text": "El IBI se paga "}

event: token
data: {"text": "entre el 1 de mayo y el 30 de junio."}

event: citation
data: {"source": "Ordenanza Fiscal 1", "url": "...", "page": 4}

event: action
data: {"type": "suggest", "label": "Domiciliar pago", "deeplink": "..."}

event: done
data: {"finish_reason": "stop", "tokens": {"in": 18, "out": 87}, "confidence": 0.94}
```

## 7.5 Autenticación e identidad

- **Sesiones anónimas** firmadas con JWT (HS256 + secreto rotado en Vault, TTL 10 min, refresco automático).
- **Sesiones identificadas** (Fase 2) con **Cl@ve OIDC** o **certificado digital** mediante el WAF que termina mTLS.
- **No** se almacenan tokens en localStorage; se utilizan **HttpOnly + SameSite=Strict** cookies o el almacenamiento seguro del SO en móvil.

## 7.6 Diseño conversacional (UX)

| Principio | Concreción |
|---|---|
| Tono institucional, cercano, no infantil | "Buenas, ¿en qué puedo ayudarle?" — siempre de usted en el primer turno |
| Aviso obligatorio inicial | "Soy un asistente automático del Ayuntamiento. No tomo decisiones administrativas." |
| Respuestas con cita | Toda afirmación factual incluye fuente y enlace |
| Sugerencias proactivas | "¿Le ayudo a pedir cita?", "¿Quiere reportar una incidencia?" |
| Brevedad escalable | Respuesta corta + botón "Quiero más detalle" |
| Salida limpia | "¿He resuelto su consulta? 👍/👎" |
| Errores con dignidad | "No tengo esa información actualizada. Puedo derivarle al 010." |

## 7.7 Notificaciones

- **Push**: recordatorios de cita, actualización de incidencia, novedades importantes (opt-in).
- **Email**: confirmación de cita con QR + .ics adjunto.
- **SMS**: solo para recordatorios críticos (uso limitado por coste y RGPD).

## 7.8 Analítica y métricas (privacidad-respetuosas)

- **Analítica propia** en **Plausible** o **Matomo** self-hosted.
- **Sin cookies de tracking**, sin perfilado, sin envío a Google/Meta.
- Eventos agregados con **differential privacy**.
- Tablero público resumido (sin PII): número de consultas, top intenciones, satisfacción.

## 7.9 Internacionalización (preparada para Fase 2)

Aunque el alcance inicial es solo español, el sistema queda preparado para:

- Lenguas cooficiales mediante salamandraTA-7b-instruct.
- Inglés/francés mediante Salamandra base + adaptador LoRA específico.
- Lectura fácil mediante fine-tuning específico y validación con Plena Inclusión.

## 7.10 Distribución y mantenimiento

| Aspecto | Web | iOS | Android |
|---|---|---|---|
| Distribución | CDN del ayuntamiento + versión congelada | App Store | Google Play (+ AppGallery opcional) |
| Versionado | Semver, *progressive enhancement* | Semver | Semver |
| Actualizaciones | Inmediatas (carga diferida) | Mensuales con Phased Release | Mensuales con Staged Rollout |
| Compatibilidad mínima | Navegadores con Web Components nativos (Chrome 90+, Firefox 90+, Safari 16+, Edge 90+) | iOS 16+ | Android 8+ |
| Política de soporte | 2 versiones anteriores | 2 versiones de iOS | 3 versiones de Android |

## 7.11 Pruebas de canal

| Tipo de prueba | Frecuencia |
|---|---|
| E2E (Playwright + Maestro/Patrol) | En cada PR |
| Accesibilidad automatizada (Axe, Espresso a11y) | En cada PR |
| Accesibilidad humana (con usuarios reales) | Trimestral |
| Pen-test móvil (MASVS) | Anual + tras cambio mayor |
| Pen-test web (OWASP ASVS L3) | Anual + tras cambio mayor |
| Carga y *stress* | Antes de cada release mayor |
