export class SSEConnection {
  private eventSource: EventSource | null = null
  private url: string
  private onMessage: (data: string) => void
  private onError: (error: Event) => void
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null
  private maxRetries = 5
  private retryCount = 0

  constructor(
    url: string,
    onMessage: (data: string) => void,
    onError?: (error: Event) => void
  ) {
    this.url = url
    this.onMessage = onMessage
    this.onError = onError || (() => {})
  }

  connect() {
    const token = localStorage.getItem('token')
    const url = token ? `${this.url}?token=${token}` : this.url
    this.eventSource = new EventSource(url)

    this.eventSource.onmessage = (event) => {
      this.retryCount = 0
      this.onMessage(event.data)
    }

    this.eventSource.onerror = (error) => {
      this.onError(error)
      this.eventSource?.close()
      this.scheduleReconnect()
    }
  }

  private scheduleReconnect() {
    if (this.retryCount >= this.maxRetries) return
    this.retryCount++
    const delay = Math.min(1000 * Math.pow(2, this.retryCount), 30000)
    this.reconnectTimer = setTimeout(() => this.connect(), delay)
  }

  close() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    this.eventSource?.close()
    this.eventSource = null
  }
}
