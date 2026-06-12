export function isValidHost(host: string): boolean {
  const ipPattern = /^(\d{1,3}\.){3}\d{1,3}$/
  const hostnamePattern = /^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*$/
  return ipPattern.test(host) || hostnamePattern.test(host)
}

export function isValidPort(port: number): boolean {
  return Number.isInteger(port) && port > 0 && port <= 65535
}

export function isValidWorkdir(workdir: string): boolean {
  return /^\/[a-zA-Z0-9\/._-]*$/.test(workdir)
}

export function isValidFileName(name: string): boolean {
  return /^[a-zA-Z0-9._-]+$/.test(name) && !name.includes('..') && !name.includes('/')
}

export function hasDangerousCharacters(value: string): boolean {
  const forbidden = [';', '&&', '|', '`', '$(', '>', '<']
  return forbidden.some((char) => value.includes(char))
}
