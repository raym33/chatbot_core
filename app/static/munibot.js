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
            <div class="muted">Respuestas con fuentes cuando existan.</div>
            <button class="submit" type="submit">Enviar</button>
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
