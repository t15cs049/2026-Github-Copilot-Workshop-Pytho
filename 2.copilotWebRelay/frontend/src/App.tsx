import { useEffect, useRef, useState, useCallback } from 'react'
import { Terminal } from '@xterm/xterm'
import { FitAddon } from '@xterm/addon-fit'
import '@xterm/xterm/css/xterm.css'
import './App.css'

function App() {
  const terminalRef = useRef<HTMLDivElement>(null)
  const terminalInstanceRef = useRef<Terminal | null>(null)
  const fitAddonRef = useRef<FitAddon | null>(null)
  const wsRef = useRef<WebSocket | null>(null)

  const [isConnected, setIsConnected] = useState(false)
  const [sessionActive, setSessionActive] = useState(false)

  // WebSocket経由でリサイズを送信
  const sendResize = useCallback(() => {
    const terminal = terminalInstanceRef.current
    const ws = wsRef.current
    if (terminal && ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: 'resize',
        cols: terminal.cols,
        rows: terminal.rows,
      }))
    }
  }, [])

  // ターミナルの初期化
  useEffect(() => {
    if (!terminalRef.current || terminalInstanceRef.current) return

    const terminal = new Terminal({
      theme: {
        background: '#1e1e1e',
        foreground: '#f0f0f0',
        cursor: '#f0f0f0',
      },
      fontSize: 14,
      fontFamily: 'Menlo, Monaco, "Courier New", monospace',
      cursorBlink: true,
    })

    const fitAddon = new FitAddon()
    terminal.loadAddon(fitAddon)
    terminal.open(terminalRef.current)
    fitAddon.fit()

    terminalInstanceRef.current = terminal
    fitAddonRef.current = fitAddon

    // ウェルカムメッセージ
    terminal.writeln('Copilot Web Relay Terminal')
    terminal.writeln('Click "Start Session" to begin.')
    terminal.writeln('')

    // ターミナル入力をWebSocket経由で送信
    const onDataDisposable = terminal.onData((data) => {
      const ws = wsRef.current
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
          type: 'input',
          payload: data,
        }))
      }
    })

    return () => {
      onDataDisposable.dispose()
      terminal.dispose()
      terminalInstanceRef.current = null
      fitAddonRef.current = null
    }
  }, [])

  // ResizeObserver でコンテナサイズ変更を監視
  useEffect(() => {
    const container = terminalRef.current
    if (!container) return

    const resizeObserver = new ResizeObserver(() => {
      const fitAddon = fitAddonRef.current
      if (fitAddon) {
        fitAddon.fit()
        sendResize()
      }
    })

    resizeObserver.observe(container)

    return () => {
      resizeObserver.disconnect()
    }
  }, [sendResize])

  // WebSocket接続
  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/ws`
    const ws = new WebSocket(wsUrl)
    wsRef.current = ws

    ws.onopen = () => {
      // StrictMode対応: 古い接続のコールバックを無視
      if (wsRef.current === ws) {
        setIsConnected(true)
        console.log('WebSocket connected')
      }
    }

    ws.onclose = () => {
      if (wsRef.current === ws) {
        setIsConnected(false)
        setSessionActive(false)
        wsRef.current = null
        console.log('WebSocket disconnected')
      }
    }

    ws.onerror = (error) => {
      if (wsRef.current === ws) {
        console.error('WebSocket error:', error)
        setIsConnected(false)
      }
    }

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        const terminal = terminalInstanceRef.current

        switch (message.type) {
          case 'output':
            if (terminal && message.payload) {
              terminal.write(message.payload)
            }
            break
          case 'status':
            if (message.state === 'running') {
              setSessionActive(true)
            } else if (message.state === 'stopped' || message.state === 'error') {
              setSessionActive(false)
            }
            if (terminal && message.payload) {
              terminal.writeln(`\r\n[Status] ${message.payload}`)
            }
            break
          default:
            console.log('Unknown message type:', message.type)
        }
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e)
      }
    }

    return () => {
      if (wsRef.current === ws) {
        wsRef.current = null
      }
      ws.close()
    }
  }, [])

  const handleStartSession = () => {
    const ws = wsRef.current
    const terminal = terminalInstanceRef.current
    if (ws && ws.readyState === WebSocket.OPEN && terminal) {
      ws.send(JSON.stringify({
        type: 'session',
        action: 'start',
        cols: terminal.cols,
        rows: terminal.rows,
      }))
    }
  }

  const handleStopSession = () => {
    const ws = wsRef.current
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: 'session',
        action: 'stop',
      }))
    }
  }

  return (
    <div className="app">
      <div className="toolbar">
        <h1>Copilot Web Relay</h1>

        <div className="status-indicator">
          <span className={`dot ${isConnected ? 'connected' : 'disconnected'}`} />
          <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
        </div>

        {!sessionActive ? (
          <button className="start" onClick={handleStartSession} disabled={!isConnected}>
            Start Session
          </button>
        ) : (
          <button className="stop" onClick={handleStopSession} disabled={!isConnected}>
            Stop Session
          </button>
        )}
      </div>

      <div className="terminal-container" ref={terminalRef} />
    </div>
  )
}

export default App
