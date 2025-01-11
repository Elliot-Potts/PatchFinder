import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface Port {
  port: string
  description: string
  vlan: string
  last_input: string
  input_packets: string
  output_packets: string
  usage_percentage: number
}

export function DisconnectedPorts({ ports }: { ports: Port[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Non-connect Switchports</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Port</TableHead>
              <TableHead>Description</TableHead>
              <TableHead>VLAN</TableHead>
              <TableHead>Last Input</TableHead>
              <TableHead>Input Packets</TableHead>
              <TableHead>Output Packets</TableHead>
              <TableHead>Percent Use</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {ports.map((port) => (
              <TableRow key={port.port}>
                <TableCell className="font-mono">{port.port}</TableCell>
                <TableCell className="text-muted-foreground">{port.description}</TableCell>
                <TableCell>{port.vlan}</TableCell>
                <TableCell>{port.last_input}</TableCell>
                <TableCell>{port.input_packets}</TableCell>
                <TableCell>{port.output_packets}</TableCell>
                <TableCell>{port.usage_percentage}%</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
} 