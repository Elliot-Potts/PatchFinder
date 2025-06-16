import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"

interface ConnectionFormProps {
  onConnect: (data: { ip: string; username: string; password: string }) => void
  isLoading: boolean
}

export function ConnectionForm({ onConnect, isLoading }: ConnectionFormProps) {
  const [formData, setFormData] = useState({
    ip: "",
    username: "",
    password: "",
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onConnect(formData)
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Connect to a switch</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="ip">IP Address</Label>
            <Input
              id="ip"
              placeholder="192.168.1.1"
              value={formData.ip}
              onChange={(e) => setFormData({ ...formData, ip: e.target.value })}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="username">Username</Label>
            <Input
              id="username"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              required
            />
          </div>
          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? "Connecting..." : "Connect"}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
} 