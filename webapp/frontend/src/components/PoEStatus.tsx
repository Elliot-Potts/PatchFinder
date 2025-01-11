import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface PoEEntry {
  switch_no: string
  available: string
  used: string
  free: string
}

export function PoEStatus({ data }: { data: PoEEntry[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>PoE Details</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Switch No.</TableHead>
              <TableHead>Available</TableHead>
              <TableHead>Used</TableHead>
              <TableHead>Free</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((entry) => (
              <TableRow key={entry.switch_no}>
                <TableCell>{entry.switch_no}</TableCell>
                <TableCell>{entry.available}</TableCell>
                <TableCell>{entry.used}</TableCell>
                <TableCell className={entry.free === "n/a" || entry.free === "0.0" ? "text-destructive" : ""}>
                  {entry.free}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
} 