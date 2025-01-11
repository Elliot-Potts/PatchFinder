import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface SwitchInfoProps {
  hostname: string
  uptime: string
  ip: string
}

export function SwitchInfo({ hostname, uptime, ip }: SwitchInfoProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Switch Information</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        <div><span className="font-semibold">Hostname:</span> {hostname}</div>
        <div><span className="font-semibold">IP Address:</span> {ip}</div>
        <div><span className="font-semibold">Uptime:</span> {uptime}</div>
      </CardContent>
    </Card>
  )
} 