import { useState } from "react"
import { ConnectionForm } from "@/components/ConnectionForm"
import { SwitchInfo } from "@/components/SwitchInfo"
import { DisconnectedPorts } from "@/components/DisconnectedPorts"
import { PoEStatus } from "@/components/PoEStatus"
import { useToast } from "@/hooks/use-toast"
import { Toaster } from "@/components/ui/toaster"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface Port {
  port: string
  description: string
  vlan: string
  last_input: string
  input_packets: string
  output_packets: string
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

function App() {
  const [isLoading, setIsLoading] = useState(false)
  const [switchData, setSwitchData] = useState<SwitchData | null>(null)
  const [connectedIp, setConnectedIp] = useState<string>("")
  const { toast } = useToast()

  const handleConnect = async (data: { ip: string; username: string; password: string }) => {
    setIsLoading(true)
    try {
      const response = await fetch("http://localhost:8000/api/connect", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
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
            <div className={`${!switchData ? "max-w-[400px] w-full" : ""}`}>
              <ConnectionForm onConnect={handleConnect} isLoading={isLoading} />
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

export default App
