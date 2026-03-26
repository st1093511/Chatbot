import { useState, useRef, useEffect } from "react"
import axios from "axios"

const API = "http://127.0.0.1:8000"

const BADGE_COLORS = {
  RAG:     { bg: "#1a3a2a", color: "#4ade80", label: "RAG" },
  SQL:     { bg: "#1a2a3a", color: "#60a5fa", label: "Text-to-SQL" },
  CRUD:    { bg: "#2a1a3a", color: "#c084fc", label: "CRUD" },
  UNKNOWN: { bg: "#2a2a1a", color: "#facc15", label: "Unknown" },
}

function Badge({ intent }) {
  const s = BADGE_COLORS[intent] || BADGE_COLORS.UNKNOWN
  return (
    <span style={{
      background: s.bg, color: s.color,
      fontSize: "11px", fontWeight: 600,
      padding: "2px 10px", borderRadius: "20px",
      letterSpacing: "0.05em"
    }}>{s.label}</span>
  )
}

function SqlBlock({ sql }) {
  return (
    <div style={{
      background: "#1e2030", border: "1px solid #2d3148",
      borderRadius: 8, padding: "8px 12px",
      fontFamily: "monospace", fontSize: 12,
      color: "#94a3b8", whiteSpace: "pre-wrap", wordBreak: "break-all"
    }}>
      <span style={{ color: "#64748b", fontSize: 10, display: "block", marginBottom: 4 }}>
        SQL που εκτελέστηκε
      </span>
      {sql}
    </div>
  )
}

function Message({ msg }) {
  const isUser = msg.role === "user"
  return (
    <div style={{
      display: "flex", justifyContent: isUser ? "flex-end" : "flex-start",
      marginBottom: "16px", gap: "10px", alignItems: "flex-start"
    }}>
      {!isUser && (
        <div style={{
          width: 32, height: 32, borderRadius: 8,
          background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
          display: "flex", alignItems: "center",
          justifyContent: "center", fontSize: 14, flexShrink: 0
        }}>🤖</div>
      )}
      <div style={{ maxWidth: "72%", display: "flex", flexDirection: "column", gap: 6 }}>
        {msg.intent && <Badge intent={msg.intent} />}
        {msg.sql && <SqlBlock sql={msg.sql} />}
        <div style={{
          background: isUser ? "linear-gradient(135deg, #6366f1, #8b5cf6)" : "#1e2030",
          color: isUser ? "#fff" : "#e2e8f0",
          padding: "10px 14px",
          borderRadius: isUser ? "18px 18px 4px 18px" : "18px 18px 18px 4px",
          fontSize: 14, lineHeight: 1.6,
          border: isUser ? "none" : "1px solid #2d3148",
          whiteSpace: "pre-wrap"
        }}>
          {msg.content}
          {msg.streaming && (
            <span style={{
              display: "inline-block", width: 2, height: 14,
              background: "#6366f1", marginLeft: 3,
              verticalAlign: "text-bottom",
              animation: "blink 1s step-end infinite"
            }} />
          )}
          {msg.stopped && (
            <span style={{ fontSize: 11, color: "#64748b", marginLeft: 6 }}>
              ◼ διακόπηκε
            </span>
          )}
        </div>
      </div>
    </div>
  )
}

function UploadedFile({ name, onRemove }) {
  return (
    <div style={{
      display: "flex", alignItems: "center", gap: 6,
      background: "#1e2030", border: "1px solid #2d3148",
      borderRadius: 20, padding: "3px 10px 3px 8px",
      fontSize: 12, color: "#94a3b8"
    }}>
      <span>📄</span>
      <span>{name}</span>
      <button onClick={onRemove} style={{
        background: "none", border: "none", color: "#64748b",
        cursor: "pointer", fontSize: 14, lineHeight: 1, padding: 0
      }}>×</button>
    </div>
  )
}

// ── Ιστορικό sidebar ─────────────────────────────────────
function HistorySidebar({ sessions, activeId, onSelect, onNew, onDelete }) {
  return (
    <div style={{
      width: 220, flexShrink: 0,
      background: "#0d0f18",
      borderRight: "1px solid #1e2030",
      display: "flex", flexDirection: "column",
      height: "100vh", overflow: "hidden"
    }}>
      <div style={{
        padding: "16px 12px 10px",
        borderBottom: "1px solid #1e2030",
        display: "flex", alignItems: "center", justifyContent: "space-between"
      }}>
        <span style={{ fontSize: 13, fontWeight: 600, color: "#94a3b8" }}>
          Ιστορικό
        </span>
        <button onClick={onNew} style={{
          background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
          border: "none", borderRadius: 6, color: "#fff",
          fontSize: 11, fontWeight: 600, padding: "4px 10px",
          cursor: "pointer"
        }}>+ Νέα</button>
      </div>

      <div style={{ flex: 1, overflowY: "auto", padding: "8px 6px" }}>
        {sessions.length === 0 && (
          <div style={{ fontSize: 12, color: "#334155", textAlign: "center", marginTop: 20 }}>
            Καμία συνομιλία
          </div>
        )}
        {sessions.map(s => (
          <div
            key={s.id}
            onClick={() => onSelect(s.id)}
            style={{
              padding: "8px 10px",
              borderRadius: 8,
              marginBottom: 4,
              cursor: "pointer",
              background: s.id === activeId ? "#1e2030" : "transparent",
              border: s.id === activeId ? "1px solid #2d3148" : "1px solid transparent",
              display: "flex", alignItems: "center", justifyContent: "space-between",
              transition: "all 0.15s"
            }}
          >
            <div style={{ flex: 1, overflow: "hidden" }}>
              <div style={{
                fontSize: 12, color: "#e2e8f0",
                whiteSpace: "nowrap", overflow: "hidden",
                textOverflow: "ellipsis"
              }}>
                {s.title}
              </div>
              <div style={{ fontSize: 10, color: "#475569", marginTop: 2 }}>
                {s.date}
              </div>
            </div>
            <button
              onClick={e => { e.stopPropagation(); onDelete(s.id) }}
              style={{
                background: "none", border: "none",
                color: "#475569", cursor: "pointer",
                fontSize: 14, padding: "0 2px", flexShrink: 0
              }}
            >×</button>
          </div>
        ))}
      </div>
    </div>
  )
}

// ── Βοηθητικές ───────────────────────────────────────────
function makeId() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2)
}

function makeSession(firstMessage) {
  return {
    id: makeId(),
    title: firstMessage.slice(0, 40) || "Νέα συνομιλία",
    date: new Date().toLocaleDateString("el-GR"),
    messages: []
  }
}

// ── Κύριο component ──────────────────────────────────────
export default function App() {
  const [sessions, setSessions]           = useState([])
  const [activeId, setActiveId]           = useState(null)
  const [input, setInput]                 = useState("")
  const [loading, setLoading]             = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState([])
  const bottomRef  = useRef(null)
  const fileRef    = useRef(null)
  const abortRef   = useRef(null)  // ← για διακοπή

  // Τρέχουσα συνομιλία
  const activeSession = sessions.find(s => s.id === activeId)
  const messages = activeSession?.messages || []

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  // ── Helpers ──────────────────────────────────────────
  function setMessages(updater) {
    setSessions(prev => prev.map(s =>
      s.id === activeId
        ? { ...s, messages: typeof updater === "function" ? updater(s.messages) : updater }
        : s
    ))
  }

  function newSession() {
    const s = makeSession("Νέα συνομιλία")
    setSessions(prev => [s, ...prev])
    setActiveId(s.id)
  }

  function deleteSession(id) {
    setSessions(prev => prev.filter(s => s.id !== id))
    if (activeId === id) setActiveId(null)
  }

  // ── Διακοπή ─────────────────────────────────────────
  function handleStop() {
    if (abortRef.current) {
      abortRef.current.abort()
    }
  }

  // ── File upload ──────────────────────────────────────
  async function handleFileUpload(e) {
    const file = e.target.files[0]
    if (!file) return

    // Δημιούργησε session αν δεν υπάρχει
    let currentId = activeId
    if (!currentId) {
      const s = makeSession(`Αρχείο: ${file.name}`)
      setSessions(prev => [s, ...prev])
      setActiveId(s.id)
      currentId = s.id
    }

    const formData = new FormData()
    formData.append("file", file)

    try {
      const res = await axios.post(`${API}/upload`, formData)
      setUploadedFiles(prev => [...prev, file.name])
      setSessions(prev => prev.map(s =>
        s.id === currentId
          ? { ...s, messages: [...s.messages, {
              role: "assistant", intent: null,
              content: `✅ ${res.data.message}`
            }]}
          : s
      ))
    } catch (err) {
      setSessions(prev => prev.map(s =>
        s.id === currentId
          ? { ...s, messages: [...s.messages, {
              role: "assistant",
              content: `❌ Σφάλμα upload: ${err.message}`
            }]}
          : s
      ))
    }
    e.target.value = ""
  }

  // ── Chat με streaming + διακοπή ──────────────────────
  async function handleSend() {
    if (!input.trim() || loading) return
    const question = input.trim()
    setInput("")
    setLoading(true)

    // Δημιούργησε session αν δεν υπάρχει
    let currentId = activeId
    if (!currentId) {
      const s = makeSession(question)
      setSessions(prev => [s, ...prev])
      setActiveId(s.id)
      currentId = s.id
    }

    // Πρόσθεσε μήνυμα χρήστη + placeholder
    setSessions(prev => prev.map(s =>
      s.id === currentId ? { ...s, messages: [
        ...s.messages,
        { role: "user", content: question },
        { role: "assistant", content: "", streaming: true, intent: null, sql: null, stopped: false }
      ]} : s
    ))

    // AbortController για διακοπή
    const controller = new AbortController()
    abortRef.current = controller

    try {
      const formData = new FormData()
      formData.append("question", question)

      const response = await fetch(`${API}/chat`, {
        method: "POST",
        body: formData,
        signal: controller.signal  // ← σύνδεση με abort
      })

      const reader  = response.body.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const text  = decoder.decode(value)
        const lines = text.split("\n")

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue
          const raw = line.slice(6).trim()
          if (!raw) continue

          let parsed
          try { parsed = JSON.parse(raw) } catch { continue }

          if (parsed.type === "done") {
            setSessions(prev => prev.map(s =>
              s.id === currentId ? { ...s, messages: s.messages.map((m, i) =>
                i === s.messages.length - 1 ? { ...m, streaming: false } : m
              )} : s
            ))
            continue
          }

          if (parsed.type === "intent") {
            setSessions(prev => prev.map(s =>
              s.id === currentId ? { ...s, messages: s.messages.map((m, i) =>
                i === s.messages.length - 1 ? { ...m, intent: parsed.value } : m
              )} : s
            ))
            continue
          }

          if (parsed.type === "sql") {
            setSessions(prev => prev.map(s =>
              s.id === currentId ? { ...s, messages: s.messages.map((m, i) =>
                i === s.messages.length - 1 ? { ...m, sql: parsed.value } : m
              )} : s
            ))
            continue
          }

          if (parsed.type === "text") {
            setSessions(prev => prev.map(s =>
              s.id === currentId ? { ...s, messages: s.messages.map((m, i) =>
                i === s.messages.length - 1
                  ? { ...m, content: m.content + parsed.value }
                  : m
              )} : s
            ))
          }
        }
      }
    } catch (err) {
      // Διακοπή από χρήστη
      if (err.name === "AbortError") {
        setSessions(prev => prev.map(s =>
          s.id === currentId ? { ...s, messages: s.messages.map((m, i) =>
            i === s.messages.length - 1
              ? { ...m, streaming: false, stopped: true }
              : m
          )} : s
        ))
      } else {
        setSessions(prev => prev.map(s =>
          s.id === currentId ? { ...s, messages: s.messages.map((m, i) =>
            i === s.messages.length - 1
              ? { ...m, content: `❌ Σφάλμα: ${err.message}`, streaming: false }
              : m
          )} : s
        ))
      }
    }

    abortRef.current = null
    setLoading(false)
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div style={{ display: "flex", height: "100vh", overflow: "hidden" }}>

      {/* Sidebar */}
      <HistorySidebar
        sessions={sessions}
        activeId={activeId}
        onSelect={setActiveId}
        onNew={newSession}
        onDelete={deleteSession}
      />

      {/* Κύρια περιοχή */}
      <div style={{
        flex: 1, display: "flex", flexDirection: "column",
        maxWidth: 800, margin: "0 auto", padding: "0 16px",
        width: "100%"
      }}>

        {/* Header */}
        <div style={{
          padding: "16px 0 12px", borderBottom: "1px solid #1e2030",
          display: "flex", alignItems: "center", gap: 12
        }}>
          <div style={{
            width: 38, height: 38, borderRadius: 10,
            background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
            display: "flex", alignItems: "center",
            justifyContent: "center", fontSize: 18
          }}>🧠</div>
          <div>
            <div style={{ fontWeight: 600, fontSize: 16 }}>Smart DB Assistant</div>
            <div style={{ fontSize: 12, color: "#64748b" }}>RAG · Text-to-SQL · GPT-4o-mini</div>
          </div>
          <div style={{ marginLeft: "auto", display: "flex", gap: 6, flexWrap: "wrap" }}>
            {uploadedFiles.map((f, i) => (
              <UploadedFile key={i} name={f} onRemove={() =>
                setUploadedFiles(prev => prev.filter((_, j) => j !== i))
              } />
            ))}
          </div>
        </div>

        {/* Messages */}
        <div style={{ flex: 1, overflowY: "auto", padding: "20px 0" }}>
          {messages.length === 0 && (
            <div style={{ textAlign: "center", marginTop: "20vh", lineHeight: 2 }}>
              <div style={{ fontSize: 40, marginBottom: 16 }}>🧠</div>
              <div style={{ fontWeight: 500, color: "#64748b", fontSize: 14 }}>
                Ανέβασε ένα αρχείο ή κάνε μια ερώτηση
              </div>
              <div style={{ fontSize: 12, marginTop: 8, color: "#334155" }}>
                Υποστηρίζει PDF · TXT · CSV · SQLite
              </div>
            </div>
          )}
          {messages.map((msg, i) => <Message key={i} msg={msg} />)}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div style={{
          borderTop: "1px solid #1e2030",
          padding: "12px 0 16px",
          display: "flex", flexDirection: "column", gap: 10
        }}>
          <div style={{
            display: "flex", gap: 8,
            background: "#1e2030", border: "1px solid #2d3148",
            borderRadius: 14, padding: "8px 8px 8px 16px",
            alignItems: "flex-end"
          }}>
            <button
              onClick={() => fileRef.current.click()}
              style={{
                background: "none", border: "none", color: "#64748b",
                cursor: "pointer", fontSize: 20, padding: "4px 6px",
                borderRadius: 8, flexShrink: 0, alignSelf: "center",
                transition: "color 0.2s"
              }}
              onMouseOver={e => e.target.style.color = "#6366f1"}
              onMouseOut={e  => e.target.style.color = "#64748b"}
            >📎</button>

            <input
              ref={fileRef} type="file"
              accept=".pdf,.txt,.csv,.db"
              style={{ display: "none" }}
              onChange={handleFileUpload}
            />

            <textarea
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Κάνε μια ερώτηση στα δεδομένα σου..."
              rows={1}
              style={{
                flex: 1, background: "none", border: "none",
                color: "#e2e8f0", fontSize: 14, resize: "none",
                outline: "none", lineHeight: 1.5, maxHeight: 120,
                overflowY: "auto", fontFamily: "inherit", padding: "4px 0"
              }}
            />

            {/* Κουμπί διακοπής ή αποστολής */}
            {loading ? (
              <button
                onClick={handleStop}
                style={{
                  background: "#7f1d1d",
                  border: "none", borderRadius: 10,
                  width: 36, height: 36, cursor: "pointer",
                  display: "flex", alignItems: "center",
                  justifyContent: "center", fontSize: 14,
                  flexShrink: 0, transition: "all 0.2s",
                  color: "#fca5a5"
                }}
                title="Διακοπή"
              >◼</button>
            ) : (
              <button
                onClick={handleSend}
                disabled={!input.trim()}
                style={{
                  background: !input.trim() ? "#2d3148"
                    : "linear-gradient(135deg, #6366f1, #8b5cf6)",
                  border: "none", borderRadius: 10,
                  width: 36, height: 36,
                  cursor: !input.trim() ? "not-allowed" : "pointer",
                  display: "flex", alignItems: "center",
                  justifyContent: "center", fontSize: 16,
                  flexShrink: 0, transition: "all 0.2s"
                }}
              >➤</button>
            )}
          </div>

          <div style={{ fontSize: 11, color: "#334155", textAlign: "center" }}>
            Enter για αποστολή · Shift+Enter για νέα γραμμή · 📎 για upload · ◼ για διακοπή
          </div>
        </div>
      </div>

      <style>{`
        @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
      `}</style>
    </div>
  )
}