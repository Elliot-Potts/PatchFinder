import { useState } from "react"
import { ConnectionForm } from "@/components/ConnectionForm"
import { SwitchInfo } from "@/components/SwitchInfo"
import { DisconnectedPorts } from "@/components/DisconnectedPorts"
import { PoEStatus } from "@/components/PoEStatus"
import { useToast } from "@/hooks/use-toast"
import { Toaster } from "@/components/ui/toaster"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ActionButtons } from "@/components/ActionButtons"
import { AuthProvider, useAuth } from "@/contexts/AuthContext"
import { LoginForm } from "@/components/LoginForm"

interface Port {
  port: string
  description: string
  vlan: string
  last_input: string
  input_packets: string
  output_packets: string
  usage_percentage: number
}

interface PoEEntry {
  switch_no: string
  available: string
  used: string
  free: string
}

interface SwitchData {
  hostname: string
  uptime: string
  disconnected_ports: Port[]
  poe_status: PoEEntry[] | null
  lowest_usage_interface: {
    interface: string
    usage_percentage: number
  } | null
}

function AppContent() {
  const [isLoading, setIsLoading] = useState(false)
  const [switchData, setSwitchData] = useState<SwitchData | null>(null)
  const [connectedIp, setConnectedIp] = useState<string>("")
  const { toast } = useToast()
  const [isExporting, setIsExporting] = useState(false)
  const { isAuthenticated, token } = useAuth()

  const handleConnect = async (data: { ip: string; username: string; password: string }) => {
    setIsLoading(true)
    try {
      const response = await fetch("http://localhost:8000/api/connect", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`)
      }

      const result = await response.json()
      setSwitchData(result)
      setConnectedIp(data.ip)
      toast({
        title: "Connected successfully",
        description: `Connected to ${result.hostname}`,
      })
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Connection failed",
        description: error instanceof Error ? error.message : "Unknown error occurred",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleDisconnect = async () => {
    try {
      await fetch("http://localhost:8000/api/disconnect", {
        method: "POST"
      })
      setSwitchData(null)
      setConnectedIp("")
      toast({
        title: "Disconnected",
        description: "Successfully disconnected from switch"
      })
    } catch {
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to disconnect"
      })
    }
  }

  const handleExport = async () => {
    if (!switchData) return

    setIsExporting(true)
    try {
      const content = [
        "-".repeat(103),
        `PATCHFINDER RESULTS on hostname ${switchData.hostname}`,
        "-".repeat(103),
        `Switch IP: ${connectedIp}`,
        `Switch hostname: ${switchData.hostname}`,
        `Switch uptime: ${switchData.uptime}\n`,
        "-".repeat(103),
        "Not-connect Interfaces:",
        "-".repeat(103),
        "Interface\tDescription\t\tVLAN\t\tLast Input\tPackets (in)\tPackets (out)\tPercent Use",
        switchData.disconnected_ports.map(port => 
          `${port.port.padEnd(10)}\t${port.description.padEnd(20)}\t${port.vlan.padEnd(8)}\t` +
          `${port.last_input.padEnd(12)}\t${port.input_packets.padEnd(12)}\t${port.output_packets.padEnd(12)}\t` +
          `${port.usage_percentage}%`
        ).join('\n'),
        "\n" + "-".repeat(103),
        "PoE Details:",
        "-".repeat(103),
        switchData.poe_status?.map(poe =>
          `${poe.switch_no.padEnd(10)} Available: ${poe.available.padEnd(8)} ` +
          `Used: ${poe.used.padEnd(8)} Free: ${poe.free}`
        ).join('\n') || "No PoE data available",
        "\n" + "-".repeat(103),
        "Lowest Usage Interface:",
        "-".repeat(103),
        switchData.lowest_usage_interface
          ? `Interface ${switchData.lowest_usage_interface.interface} has ` +
            `${switchData.lowest_usage_interface.usage_percentage}% the usage of the highest on the switch.`
          : "No usage data available"
      ].join('\n')

      const blob = new Blob([content], { type: 'text/plain' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${switchData.hostname}.txt`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)

      toast({
        title: "Export complete",
        description: `Saved as ${switchData.hostname}.txt`
      })
    } catch {
      toast({
        variant: "destructive",
        title: "Export failed",
        description: "Failed to export summary"
      })
    } finally {
      setIsExporting(false)
    }
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-background p-8">
        <div className="container mx-auto max-w-7xl">
          <div className="flex justify-center">
            <div className="max-w-[400px] w-full">
              <h1 className="text-4xl font-bold mb-8">PatchFinder</h1>
              <LoginForm />
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <>
      <div className="min-h-screen bg-background p-8">
        <div className="container mx-auto max-w-7xl">
          <div className={`${!switchData ? "flex justify-center" : ""}`}>
            <div className={`${!switchData ? "max-w-[400px] w-full" : ""}`}>
              <h1 className="text-4xl font-bold mb-8">PatchFinder</h1>
            </div>
          </div>
          
          <div className={`grid gap-8 ${
            switchData 
              ? "grid-cols-1 lg:grid-cols-[400px,1fr]" 
              : "place-items-center"
          }`}>
            <div className={`${!switchData ? "max-w-[400px] w-full" : "space-y-4"}`}>
              <ConnectionForm onConnect={handleConnect} isLoading={isLoading} />
              {switchData && (
                <ActionButtons
                  onDisconnect={handleDisconnect}
                  onExport={handleExport}
                  isExporting={isExporting}
                />
              )}
            </div>
            
            {switchData && (
              <div className="space-y-8">
                <SwitchInfo 
                  hostname={switchData.hostname}
                  uptime={switchData.uptime}
                  ip={connectedIp}
                />
                
                <DisconnectedPorts ports={switchData.disconnected_ports} />
                
                {switchData.poe_status && (
                  <PoEStatus data={switchData.poe_status} />
                )}
                
                {switchData.lowest_usage_interface && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Lowest Usage Interface</CardTitle>
                    </CardHeader>
                    <CardContent>
                      Interface <span className="font-semibold text-primary">{switchData.lowest_usage_interface.interface}</span> has{" "}
                      <span className="font-semibold text-primary">{switchData.lowest_usage_interface.usage_percentage}%</span>{" "}
                      the usage of the highest on the switch.
                    </CardContent>
                  </Card>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
      <Toaster />
    </>
  )
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App
