class MunibotWidget extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this.sessionId = null;
    this.ws = null;
    this.pendingAssistant = null;
    this.citations = [];
    this.lastUserMessage = null;
    this.welcomeMessage = null;
    this.disclaimer = null;
    this.voiceEnabled = true;
    this.voiceLoopActive = false;
    this.voiceTurnInFlight = false;
    this.isRecording = false;
    this.mediaStream = null;
    this.audioContext = null;
    this.inputNode = null;
    this.processor = null;
    this.silenceNode = null;
    this.recordedChunks = [];
    this.preSpeechChunks = [];
    this.speechDetected = false;
    this.speechStartedAt = 0;
    this.lastSpeechAt = 0;
    this.pendingRestartTimer = null;
    this.currentAudio = null;
    this.vadThreshold = 0.018;
    this.vadSilenceMs = 1100;
    this.vadMinSpeechMs = 350;
    this.vadMaxSpeechMs = 12000;
    this.vadPrebufferChunks = 4;
  }

  connectedCallback() {
    this.endpoint = (this.getAttribute("endpoint") || window.MUNIBOT_ENDPOINT || window.location.origin).replace(/\/$/, "");
    this.title = this.getAttribute("title") || "Asistente";
    this.accent = this.getAttribute("accent") || "#0A4A73";
    this.position = this.getAttribute("position") || "bottom-right";
    this.eyebrow = this.getAttribute("eyebrow") || "IA asistida";
    this.initialDisclaimer = this.getAttribute("disclaimer") || "Respuestas asistidas por documentos y reglas de seguridad.";
    this.placeholder = this.getAttribute("placeholder") || "Escriba su consulta";
    this.render();
    this.bindEvents();
  }

  render() {
    const side = this.position.includes("left") ? "left: 24px;" : "right: 24px;";
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          font-family: "SF Pro Text", "Segoe UI", sans-serif;
          color: #13212c;
        }
        .launcher {
          position: fixed;
          ${side}
          bottom: 24px;
          width: 64px;
          height: 64px;
          border-radius: 999px;
          border: none;
          background: linear-gradient(135deg, ${this.accent}, #0d6b8d);
          color: white;
          font-size: 28px;
          box-shadow: 0 18px 40px rgba(10, 74, 115, 0.28);
          cursor: pointer;
          z-index: 99999;
        }
        .panel {
          position: fixed;
          ${side}
          bottom: 100px;
          width: min(390px, calc(100vw - 24px));
          height: min(72vh, 680px);
          background: linear-gradient(180deg, #f6fbff 0%, #ffffff 22%);
          border: 1px solid rgba(10, 74, 115, 0.14);
          border-radius: 24px;
          box-shadow: 0 28px 70px rgba(13, 29, 42, 0.22);
          display: none;
          overflow: hidden;
          z-index: 99999;
        }
        .panel.open { display: grid; grid-template-rows: auto 1fr auto; }
        .header {
          padding: 18px 20px 14px;
          background: linear-gradient(135deg, ${this.accent}, #0d6b8d);
          color: white;
        }
        .eyebrow {
          opacity: 0.8;
          font-size: 12px;
          letter-spacing: 0.06em;
          text-transform: uppercase;
        }
        .title {
          font-size: 18px;
          font-weight: 700;
          margin-top: 4px;
        }
        .disclaimer {
          margin-top: 10px;
          font-size: 12px;
          line-height: 1.4;
          opacity: 0.92;
        }
        .messages {
          padding: 16px;
          overflow: auto;
          display: flex;
          flex-direction: column;
          gap: 12px;
          background:
            radial-gradient(circle at top right, rgba(10, 74, 115, 0.08), transparent 35%),
            linear-gradient(180deg, rgba(255,255,255,0.95), rgba(245,250,253,0.95));
        }
        .bubble {
          padding: 12px 14px;
          border-radius: 18px;
          max-width: 85%;
          line-height: 1.45;
          font-size: 14px;
          white-space: pre-wrap;
        }
        .bubble.user {
          align-self: end;
          background: #0f6c90;
          color: white;
          border-bottom-right-radius: 6px;
        }
        .bubble.assistant {
          align-self: start;
          background: white;
          border: 1px solid rgba(10, 74, 115, 0.12);
          border-bottom-left-radius: 6px;
        }
        .citations {
          margin-top: 10px;
          display: grid;
          gap: 8px;
        }
        .citation {
          border-radius: 12px;
          border: 1px solid rgba(10, 74, 115, 0.12);
          background: #f5fbff;
          padding: 9px 10px;
          font-size: 12px;
        }
        .actions {
          margin-top: 10px;
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }
        .action {
          border: none;
          border-radius: 999px;
          padding: 8px 12px;
          background: rgba(10, 74, 115, 0.08);
          color: #0a4a73;
          cursor: pointer;
          font-size: 12px;
          font-weight: 600;
        }
        form {
          padding: 14px;
          border-top: 1px solid rgba(10, 74, 115, 0.12);
          background: white;
          display: grid;
          gap: 10px;
        }
        textarea {
          resize: none;
          min-height: 72px;
          border-radius: 16px;
          border: 1px solid rgba(10, 74, 115, 0.18);
          padding: 12px 14px;
          font: inherit;
          outline: none;
        }
        .footer {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 10px;
        }
        .controls {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
        }
        .control {
          border: 1px solid rgba(10, 74, 115, 0.15);
          border-radius: 999px;
          background: white;
          color: #0a4a73;
          padding: 8px 12px;
          font: inherit;
          font-size: 12px;
          font-weight: 700;
          cursor: pointer;
        }
        .control.active {
          background: rgba(10, 74, 115, 0.08);
        }
        .submit {
          border: none;
          border-radius: 999px;
          background: ${this.accent};
          color: white;
          padding: 10px 16px;
          font: inherit;
          font-weight: 700;
          cursor: pointer;
        }
        .muted {
          font-size: 12px;
          color: #5d6a74;
        }
        .muted.voice-status.active {
          color: #0a4a73;
          font-weight: 700;
        }
      </style>
      <button class="launcher" aria-label="Abrir asistente">M</button>
      <section class="panel" role="dialog" aria-label="${this.title}">
        <header class="header">
          <div class="eyebrow">${this.eyebrow}</div>
          <div class="title">${this.title}</div>
          <div class="disclaimer">${this.initialDisclaimer}</div>
        </header>
        <div class="messages"></div>
        <form>
          <textarea placeholder="${this.placeholder}"></textarea>
          <div class="footer">
            <div class="controls">
              <button class="control voice-toggle active" type="button">Voz on</button>
              <button class="control mic-toggle" type="button">Hablar</button>
            </div>
            <div style="display:flex; align-items:center; gap:10px;">
              <div class="muted voice-status">Respuestas con fuentes cuando existan.</div>
              <button class="submit" type="submit">Enviar</button>
            </div>
          </div>
        </form>
      </section>
    `;
  }

  bindEvents() {
    this.launcher = this.shadowRoot.querySelector(".launcher");
    this.panel = this.shadowRoot.querySelector(".panel");
    this.form = this.shadowRoot.querySelector("form");
    this.textarea = this.shadowRoot.querySelector("textarea");
    this.messages = this.shadowRoot.querySelector(".messages");
    this.voiceToggle = this.shadowRoot.querySelector(".voice-toggle");
    this.micToggle = this.shadowRoot.querySelector(".mic-toggle");
    this.voiceStatus = this.shadowRoot.querySelector(".voice-status");

    this.launcher.addEventListener("click", async () => {
      this.panel.classList.toggle("open");
      if (this.panel.classList.contains("open")) {
        this.dispatchEvent(new CustomEvent("munibot:opened", { bubbles: true }));
        if (!this.sessionId) {
          await this.ensureSession();
          this.addAssistantMessage(this.welcomeMessage || "Hola. Estoy listo para ayudarle.");
        }
      }
    });

    this.form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const content = this.textarea.value.trim();
      if (!content) return;
      this.textarea.value = "";
      await this.ensureSession();
      this.lastUserMessage = content;
      this.addUserMessage(content);
      await this.ensureSocket();
      this.pendingAssistant = this.addAssistantMessage("");
      this.citations = [];
      this.sendChat(content, false);
    });

    this.voiceToggle.addEventListener("click", () => {
      this.voiceEnabled = !this.voiceEnabled;
      this.voiceToggle.textContent = this.voiceEnabled ? "Voz on" : "Voz off";
      this.voiceToggle.classList.toggle("active", this.voiceEnabled);
      if (!this.voiceEnabled && this.currentAudio) {
        this.currentAudio.pause();
        this.currentAudio = null;
      }
    });

    this.micToggle.addEventListener("click", async () => {
      try {
        if (this.voiceLoopActive) {
          this.stopVoiceLoop();
        } else {
          await this.startVoiceLoop();
        }
      } catch (error) {
        this.stopVoiceLoop();
        this.addAssistantMessage(this.getMicrophoneErrorMessage(error));
      }
    });
  }

  async ensureSession() {
    if (this.sessionId) return;
    const response = await fetch(`${this.endpoint}/v1/sessions`, { method: "POST" });
    const payload = await response.json();
    this.sessionId = payload.session_id;
    this.welcomeMessage = payload.welcome_message;
    this.disclaimer = payload.disclaimer;
    const disclaimer = this.shadowRoot.querySelector(".disclaimer");
    if (disclaimer && this.disclaimer) {
      disclaimer.textContent = this.disclaimer;
    }
  }

  async ensureSocket() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) return;
    const wsBase = this.endpoint.replace(/^http/, "ws");
    this.ws = new WebSocket(`${wsBase}/v1/sessions/${this.sessionId}/stream`);

    this.ws.addEventListener("message", (event) => {
      const payload = JSON.parse(event.data);
      if (payload.type === "token" && this.pendingAssistant) {
        this.pendingAssistant.textContent += payload.text;
        this.messages.scrollTop = this.messages.scrollHeight;
      }
      if (payload.type === "citation" && this.pendingAssistant) {
        this.appendCitation(payload.data);
      }
      if (payload.type === "action" && this.pendingAssistant) {
        this.appendAction(payload.data);
      }
      if (payload.type === "done") {
        this.handleAssistantDone(payload.data).catch(() => {});
        this.dispatchEvent(new CustomEvent("munibot:resolved", { detail: payload.data, bubbles: true }));
        this.pendingAssistant = null;
      }
    });

    await new Promise((resolve, reject) => {
      this.ws.addEventListener("open", resolve, { once: true });
      this.ws.addEventListener("error", reject, { once: true });
    });
  }

  addUserMessage(content) {
    const bubble = document.createElement("div");
    bubble.className = "bubble user";
    bubble.textContent = content;
    this.messages.appendChild(bubble);
    this.messages.scrollTop = this.messages.scrollHeight;
    return bubble;
  }

  addAssistantMessage(content) {
    const bubble = document.createElement("div");
    bubble.className = "bubble assistant";
    bubble.textContent = content;
    this.messages.appendChild(bubble);
    this.messages.scrollTop = this.messages.scrollHeight;
    return bubble;
  }

  sendChat(content, easyRead) {
    this.ws.send(JSON.stringify({
      content,
      channel: "web",
      context: {
        page_url: this.hasAttribute("context-url") ? window.location.href : null,
        easy_read: easyRead
      }
    }));
  }

  appendCitation(citation) {
    let wrap = this.pendingAssistant.querySelector(".citations");
    if (!wrap) {
      wrap = document.createElement("div");
      wrap.className = "citations";
      this.pendingAssistant.appendChild(wrap);
    }
    const card = document.createElement("div");
    card.className = "citation";
    card.innerHTML = `<strong>${citation.source}</strong><br>${citation.snippet}`;
    wrap.appendChild(card);
  }

  appendAction(action) {
    let wrap = this.pendingAssistant.querySelector(".actions");
    if (!wrap) {
      wrap = document.createElement("div");
      wrap.className = "actions";
      this.pendingAssistant.appendChild(wrap);
    }
    const button = document.createElement("button");
    button.type = "button";
    button.className = "action";
    button.textContent = action.label;
    button.addEventListener("click", () => {
      if (action.type === "link") {
        window.open(action.target, "_blank", "noopener");
      } else if (action.type === "escalate") {
        this.requestEscalation(action.target);
      } else if (action.type === "intent" && action.target === "easy_read" && this.lastUserMessage) {
        this.pendingAssistant = this.addAssistantMessage("");
        this.sendChat(this.lastUserMessage, true);
      }
    });
    wrap.appendChild(button);
  }

  async startVoiceLoop() {
    this.voiceLoopActive = true;
    this.updateMicButton();
    this.setVoiceStatus("Escuchando...");
    const started = await this.startListening();
    if (!started) {
      this.stopVoiceLoop();
    }
  }

  stopVoiceLoop() {
    this.voiceLoopActive = false;
    this.voiceTurnInFlight = false;
    window.clearTimeout(this.pendingRestartTimer);
    this.pendingRestartTimer = null;
    if (this.currentAudio) {
      this.currentAudio.pause();
      this.currentAudio = null;
    }
    this.resetRecordingState();
    this.updateMicButton();
    this.setVoiceStatus("Respuestas con fuentes cuando existan.");
  }

  async startListening() {
    const mediaDevices = window.navigator?.mediaDevices;
    if (!window.isSecureContext || !mediaDevices?.getUserMedia) {
      throw new Error("unsupported_media_devices");
    }
    if (!(window.AudioContext || window.webkitAudioContext)) {
      throw new Error("unsupported_audio_context");
    }

    this.resetRecordingState({ preserveLoop: true });
    this.setVoiceStatus("Pidiendo permiso al microfono...");

    this.mediaStream = await mediaDevices.getUserMedia({ audio: true });
    this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
    await this.audioContext.resume();
    this.inputNode = this.audioContext.createMediaStreamSource(this.mediaStream);
    if (!this.audioContext.createScriptProcessor) {
      throw new Error("script_processor_unavailable");
    }
    this.processor = this.audioContext.createScriptProcessor(4096, 1, 1);
    this.silenceNode = this.audioContext.createGain();
    this.silenceNode.gain.value = 0;
    this.recordedChunks = [];
    this.preSpeechChunks = [];
    this.speechDetected = false;
    this.speechStartedAt = 0;
    this.lastSpeechAt = 0;
    this.processor.onaudioprocess = (event) => {
      if (!this.voiceLoopActive || this.voiceTurnInFlight) return;
      const channel = event.inputBuffer.getChannelData(0);
      const chunk = new Float32Array(channel);
      const rms = this.computeRms(chunk);
      const now = performance.now();

      this.preSpeechChunks.push(chunk);
      if (this.preSpeechChunks.length > this.vadPrebufferChunks) {
        this.preSpeechChunks.shift();
      }

      if (rms >= this.vadThreshold) {
        if (!this.speechDetected) {
          this.speechDetected = true;
          this.speechStartedAt = now;
          this.recordedChunks = [...this.preSpeechChunks];
          this.setVoiceStatus("Le estoy escuchando...");
        }
        this.lastSpeechAt = now;
      }

      if (!this.speechDetected) {
        return;
      }

      this.recordedChunks.push(chunk);
      const speechMs = now - this.speechStartedAt;
      const silenceMs = this.lastSpeechAt ? now - this.lastSpeechAt : 0;
      if (speechMs >= this.vadMaxSpeechMs || (speechMs >= this.vadMinSpeechMs && silenceMs >= this.vadSilenceMs)) {
        this.finishVoiceTurn().catch((error) => {
          this.stopVoiceLoop();
          this.addAssistantMessage(this.getMicrophoneErrorMessage(error));
        });
      }
    };
    this.inputNode.connect(this.processor);
    this.processor.connect(this.silenceNode);
    this.silenceNode.connect(this.audioContext.destination);
    this.isRecording = true;
    this.updateMicButton();
    this.setVoiceStatus("Escuchando...");
    return true;
  }

  async finishVoiceTurn() {
    if (!this.voiceLoopActive || this.voiceTurnInFlight) return;
    this.voiceTurnInFlight = true;
    this.setVoiceStatus("Procesando...");
    const merged = this.mergeAudioBuffers(this.recordedChunks);
    const sampleRate = this.audioContext?.sampleRate || 44100;
    await this.stopListeningCapture();

    if (!merged.length) {
      this.voiceTurnInFlight = false;
      if (this.voiceLoopActive) {
        this.scheduleListeningRestart(250);
      }
      return;
    }

    const downsampled = this.resampleAudio(merged, sampleRate, 16000);
    const wavBlob = this.encodeWav(downsampled, 16000);
    const formData = new FormData();
    formData.append("audio", wavBlob, "voice.wav");

    try {
      const response = await fetch(`${this.endpoint}/v1/audio/transcriptions`, {
        method: "POST",
        body: formData
      });
      const payload = await response.json();
      const content = (payload.text || "").trim();
      if (!content) {
        this.voiceTurnInFlight = false;
        this.addAssistantMessage("No he podido entender el audio. Pruebe a repetirlo mas cerca del microfono.");
        if (this.voiceLoopActive) {
          this.scheduleListeningRestart(350);
        }
        return;
      }
      this.textarea.value = content;
      this.setVoiceStatus("Pensando...");
      this.form.requestSubmit();
    } catch (error) {
      this.voiceTurnInFlight = false;
      this.addAssistantMessage("No he podido transcribir el audio ahora mismo.");
      if (this.voiceLoopActive) {
        this.scheduleListeningRestart(500);
      }
    }
  }

  async handleAssistantDone(data) {
    const content = data?.content || "";
    try {
      if (this.voiceEnabled && content) {
        this.setVoiceStatus("Respondiendo...");
        await this.playSpeech(content);
      }
    } finally {
      this.voiceTurnInFlight = false;
      if (this.voiceLoopActive) {
        this.scheduleListeningRestart(250);
      } else {
        this.setVoiceStatus("Respuestas con fuentes cuando existan.");
      }
    }
  }

  scheduleListeningRestart(delayMs) {
    if (!this.voiceLoopActive) return;
    window.clearTimeout(this.pendingRestartTimer);
    this.pendingRestartTimer = window.setTimeout(() => {
      this.pendingRestartTimer = null;
      if (!this.voiceLoopActive || this.isRecording || this.voiceTurnInFlight) return;
      this.startListening().catch((error) => {
        this.stopVoiceLoop();
        this.addAssistantMessage(this.getMicrophoneErrorMessage(error));
      });
    }, delayMs);
  }

  async stopListeningCapture() {
    this.isRecording = false;
    this.inputNode?.disconnect();
    this.processor?.disconnect();
    this.silenceNode?.disconnect();
    this.mediaStream?.getTracks().forEach((track) => track.stop());
    this.inputNode = null;
    this.processor = null;
    this.silenceNode = null;
    this.mediaStream = null;
    if (this.audioContext) {
      await this.audioContext.close().catch(() => {});
      this.audioContext = null;
    }
    this.preSpeechChunks = [];
    this.speechDetected = false;
    this.speechStartedAt = 0;
    this.lastSpeechAt = 0;
  }

  resetRecordingState({ preserveLoop = false } = {}) {
    this.isRecording = false;
    if (!preserveLoop) {
      this.voiceLoopActive = false;
      this.voiceTurnInFlight = false;
    }
    this.inputNode?.disconnect();
    this.processor?.disconnect();
    this.silenceNode?.disconnect();
    this.mediaStream?.getTracks().forEach((track) => track.stop());
    this.recordedChunks = [];
    this.preSpeechChunks = [];
    this.inputNode = null;
    this.processor = null;
    this.silenceNode = null;
    this.mediaStream = null;
    this.speechDetected = false;
    this.speechStartedAt = 0;
    this.lastSpeechAt = 0;
    if (this.audioContext) {
      this.audioContext.close().catch(() => {});
      this.audioContext = null;
    }
    this.updateMicButton();
  }

  updateMicButton() {
    if (!this.micToggle) return;
    this.micToggle.textContent = this.voiceLoopActive ? "Parar" : "Hablar";
    this.micToggle.classList.toggle("active", this.voiceLoopActive);
  }

  setVoiceStatus(text) {
    if (!this.voiceStatus) return;
    this.voiceStatus.textContent = text;
    this.voiceStatus.classList.toggle("active", this.voiceLoopActive || this.voiceTurnInFlight);
  }

  computeRms(chunk) {
    let total = 0;
    for (let i = 0; i < chunk.length; i += 1) {
      total += chunk[i] * chunk[i];
    }
    return Math.sqrt(total / chunk.length);
  }

  getMicrophoneErrorMessage(error) {
    const name = error?.name || "";
    const message = error?.message || "";
    if (message === "unsupported_media_devices") {
      return "Este navegador no permite usar el microfono desde el widget. Pruebe a recargar la pagina o a permitir el acceso al microfono.";
    }
    if (message === "unsupported_audio_context") {
      return "Este navegador no soporta la captura de audio necesaria para transcribir su voz.";
    }
    if (name === "NotAllowedError" || name === "PermissionDeniedError") {
      return "El navegador ha bloqueado el microfono. Permita el acceso al microfono y vuelva a pulsar \"Hablar\".";
    }
    if (name === "NotFoundError" || name === "DevicesNotFoundError") {
      return "No encuentro ningun microfono disponible en este equipo.";
    }
    if (name === "NotReadableError" || name === "TrackStartError") {
      return "El microfono esta ocupado por otra aplicacion o no se puede abrir ahora mismo.";
    }
    if (message === "script_processor_unavailable") {
      return "Este navegador no soporta el modo de grabacion necesario para transcribir audio.";
    }
    return "No he podido activar el microfono. Revise permisos del navegador y vuelva a intentarlo.";
  }

  mergeAudioBuffers(chunks) {
    const totalLength = chunks.reduce((sum, chunk) => sum + chunk.length, 0);
    const merged = new Float32Array(totalLength);
    let offset = 0;
    for (const chunk of chunks) {
      merged.set(chunk, offset);
      offset += chunk.length;
    }
    return merged;
  }

  resampleAudio(input, fromRate, toRate) {
    if (fromRate === toRate) return input;
    const ratio = fromRate / toRate;
    const newLength = Math.max(1, Math.round(input.length / ratio));
    const output = new Float32Array(newLength);
    for (let i = 0; i < newLength; i += 1) {
      const position = i * ratio;
      const left = Math.floor(position);
      const right = Math.min(left + 1, input.length - 1);
      const alpha = position - left;
      output[i] = input[left] * (1 - alpha) + input[right] * alpha;
    }
    return output;
  }

  encodeWav(samples, sampleRate) {
    const buffer = new ArrayBuffer(44 + samples.length * 2);
    const view = new DataView(buffer);
    const writeString = (offset, value) => {
      for (let i = 0; i < value.length; i += 1) {
        view.setUint8(offset + i, value.charCodeAt(i));
      }
    };
    writeString(0, "RIFF");
    view.setUint32(4, 36 + samples.length * 2, true);
    writeString(8, "WAVE");
    writeString(12, "fmt ");
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, 1, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * 2, true);
    view.setUint16(32, 2, true);
    view.setUint16(34, 16, true);
    writeString(36, "data");
    view.setUint32(40, samples.length * 2, true);

    let offset = 44;
    for (let i = 0; i < samples.length; i += 1) {
      const sample = Math.max(-1, Math.min(1, samples[i]));
      view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7fff, true);
      offset += 2;
    }
    return new Blob([view], { type: "audio/wav" });
  }

  async playSpeech(text) {
    const response = await fetch(`${this.endpoint}/v1/audio/speech`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });
    if (!response.ok) return;
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    if (this.currentAudio) {
      this.currentAudio.pause();
    }
    this.currentAudio = new Audio(url);
    await new Promise((resolve) => {
      const finish = () => {
        URL.revokeObjectURL(url);
        resolve();
      };
      this.currentAudio.addEventListener("ended", finish, { once: true });
      this.currentAudio.addEventListener("error", finish, { once: true });
      this.currentAudio.addEventListener("pause", finish, { once: true });
      this.currentAudio.play().catch(finish);
    });
    this.currentAudio = null;
  }

  async requestEscalation(target) {
    try {
      const response = await fetch(`${this.endpoint}${target}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reason: "Solicitud manual desde el widget" })
      });
      const payload = await response.json();
      this.addAssistantMessage(`He preparado el escalado humano con ticket ${payload.ticket_id}.`);
      this.dispatchEvent(new CustomEvent("munibot:escalated", { detail: payload, bubbles: true }));
    } catch (error) {
      this.addAssistantMessage("No he podido registrar el escalado ahora mismo. Puede intentarlo de nuevo mas tarde.");
    }
  }

  open(options = {}) {
    this.panel.classList.add("open");
    if (options.message) {
      this.textarea.value = options.message;
    }
  }
}

customElements.define("munibot-widget", MunibotWidget);
