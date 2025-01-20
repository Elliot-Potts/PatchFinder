import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowDown, ArrowUp } from "lucide-react"
import { Button } from "@/components/ui/button"

interface Port {
  port: string
  description: string
  vlan: string
  last_input: string
  input_packets: string
  output_packets: string
  usage_percentage: number
}

interface DisconnectedPortsProps {
  ports: Port[]
}

type SortKey = 'port' | 'usage_percentage'  // Limit sort keys
type SortDirection = 'asc' | 'desc'

export function DisconnectedPorts({ ports }: DisconnectedPortsProps) {
  const [sortConfig, setSortConfig] = useState<{
    key: SortKey
    direction: SortDirection
  }>({
    key: 'port',
    direction: 'asc'
  })

  const sortedPorts = [...ports].sort((a, b) => {
    if (sortConfig.key === 'usage_percentage') {
      return sortConfig.direction === 'asc' 
        ? a[sortConfig.key] - b[sortConfig.key]
        : b[sortConfig.key] - a[sortConfig.key]
    }

    const aValue = String(a[sortConfig.key]).toLowerCase()
    const bValue = String(b[sortConfig.key]).toLowerCase()

    if (sortConfig.direction === 'asc') {
      return aValue.localeCompare(bValue)
    }
    return bValue.localeCompare(aValue)
  })

  const requestSort = (key: SortKey) => {
    setSortConfig(current => ({
      key,
      direction: current.key === key && current.direction === 'asc' ? 'desc' : 'asc'
    }))
  }

  const SortButton = ({ column }: { column: SortKey }) => (
    <Button
      variant="ghost"
      size="sm"
      className="h-8 px-2 lg:px-3"
      onClick={() => requestSort(column)}
    >
      {column === 'port' ? 'Port' : 'Usage'}
      {sortConfig.key === column && (
        sortConfig.direction === 'asc' 
          ? <ArrowUp className="ml-2 h-4 w-4" />
          : <ArrowDown className="ml-2 h-4 w-4" />
      )}
    </Button>
  )

  return (
    <Card>
      <CardHeader>
        <CardTitle>Disconnected Ports</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border">
          <div className="w-full overflow-auto">
            <table className="w-full caption-bottom text-sm">
              <thead>
                <tr className="border-b transition-colors hover:bg-muted/50">
                  <th className="h-12 px-4 text-left align-middle font-medium">
                    <SortButton column="port" />
                  </th>
                  <th className="h-12 px-4 text-left align-middle font-medium">
                    Description
                  </th>
                  <th className="h-12 px-4 text-left align-middle font-medium">
                    VLAN
                  </th>
                  <th className="h-12 px-4 text-left align-middle font-medium">
                    Last Input
                  </th>
                  <th className="h-12 px-4 text-left align-middle font-medium">
                    Input Packets
                  </th>
                  <th className="h-12 px-4 text-left align-middle font-medium">
                    Output Packets
                  </th>
                  <th className="h-12 px-4 text-left align-middle font-medium">
                    <SortButton column="usage_percentage" />
                  </th>
                </tr>
              </thead>
              <tbody>
                {sortedPorts.map((port, i) => (
                  <tr
                    key={port.port + i}
                    className="border-b transition-colors hover:bg-muted/50"
                  >
                    <td className="p-4 align-middle font-mono">{port.port}</td>
                    <td className="p-4 align-middle text-muted-foreground">{port.description}</td>
                    <td className="p-4 align-middle">{port.vlan}</td>
                    <td className="p-4 align-middle">{port.last_input}</td>
                    <td className="p-4 align-middle">{port.input_packets}</td>
                    <td className="p-4 align-middle">{port.output_packets}</td>
                    <td className="p-4 align-middle">{port.usage_percentage}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </CardContent>
    </Card>
  )
} 