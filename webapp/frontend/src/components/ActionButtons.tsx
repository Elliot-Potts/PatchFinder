import { Button } from "@/components/ui/button"
import { Download, LogOut } from "lucide-react"

interface ActionButtonsProps {
  onDisconnect: () => void
  onExport: () => void
  isExporting: boolean
}

export function ActionButtons({ onDisconnect, onExport, isExporting }: ActionButtonsProps) {
  return (
    <div className="flex gap-2">
      <Button 
        variant="outline" 
        onClick={onDisconnect}
        className="flex gap-2"
      >
        <LogOut className="h-4 w-4" />
        Disconnect
      </Button>
      <Button 
        onClick={onExport} 
        disabled={isExporting}
        className="flex gap-2"
      >
        <Download className="h-4 w-4" />
        {isExporting ? "Exporting..." : "Export Summary"}
      </Button>
    </div>
  )
} 